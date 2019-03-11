# -*- coding: utf-8 -*-
import logging

from openprocurement.auctions.core.plugins.awarding.v2_1.migration import (
    migrate_awarding_1_0_to_awarding_2_1
)
from openprocurement.auctions.core.traversal import Root
from openprocurement.auctions.core.utils import (
    get_plugins, get_procurement_method_types, get_now, migrate_all_document_of_tender
)

from openprocurement.api.migration import (
    BaseMigrationsRunner,
    BaseMigrationStep
)

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 1
SCHEMA_DOC = 'openprocurement_auctions_dgf_schema'
PACKAGE_ALIASES = {
    'openprocurement.auctions.rubble': ['rubbleOther', 'rubbleFinancial']
}


def get_db_schema_version(db):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    return schema_doc.get("version", SCHEMA_VERSION - 1)


def set_db_schema_version(db, version):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    schema_doc["version"] = version
    db.save(schema_doc)


def migrate_data(registry, destination=None):
    registry.app_meta.plugins
    plugins_config = registry.app_meta.plugins
    existing_plugins = get_plugins(plugins_config)
    if registry.app_meta.plugins and not any(existing_plugins):
        return
    cur_version = get_db_schema_version(registry.db)
    if cur_version == SCHEMA_VERSION:
        return cur_version
    for step in xrange(cur_version, destination or SCHEMA_VERSION):
        LOGGER.info("Migrate openprocurement auction schema from {} to {}".format(step, step + 1), extra={'MESSAGE_ID': 'migrate_data'})
        migration_func = globals().get('from{}to{}'.format(step, step + 1))
        if migration_func:
            migration_func(registry)
        set_db_schema_version(registry.db, step + 1)


def from0to1(registry):
    class Request(object):
        def __init__(self, registry):
            self.registry = registry

    results = registry.db.iterview('auctions/all', 2 ** 10, include_docs=True)

    request = Request(registry)
    root = Root(request)
    procurement_method_types = get_procurement_method_types(
        registry, ['rubbleOther', 'rubbleFinancial']
    )
    docs = []
    for i in results:
        auction = i.doc
        migrate_awarding_1_0_to_awarding_2_1(auction, procurement_method_types)
        model = registry.auction_procurementMethodTypes.get(auction['procurementMethodType'])
        if model:
            try:
                auction = model(auction)
                auction.__parent__ = root
                auction = auction.to_primitive()
            except: # pragma: no cover
                LOGGER.error("Failed migration of auction {} to schema 1.".format(auction.id), extra={'MESSAGE_ID': 'migrate_data_failed', 'AUCTION_ID': auction.id})
            else:
                auction['dateModified'] = get_now().isoformat()
                docs.append(auction)
        if len(docs) >= 2 ** 7: # pragma: no cover
            registry.db.update(docs)
            docs = []
    if docs:
        registry.db.update(docs)


class RubbleMigrationsRunner(BaseMigrationsRunner):

    SCHEMA_VERSION = 1
    SCHEMA_DOC = SCHEMA_DOC


class DocumentOfStep(BaseMigrationStep):

    def setUp(self):
        self.view = 'auctions/all'
        self.procurement_method_types = self.resources.aliases_info.get_package_aliases(
            'openprocurement.auctions.rubble'
        )

    def migrate_document(self, auction):
        if auction['procurementMethodType'] in self.procurement_method_types:
            changed = migrate_all_document_of_tender(auction)
            return auction if changed else None
        return None


MIGRATION_STEPS = (DocumentOfStep, )


def migrate(resources):
    runner = RubbleMigrationsRunner(resources)
    runner.migrate(MIGRATION_STEPS)
