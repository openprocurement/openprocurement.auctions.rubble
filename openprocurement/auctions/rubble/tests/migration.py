# -*- coding: utf-8 -*-
import unittest

from uuid import uuid4
from copy import deepcopy

from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.rubble.migration import migrate_data, get_db_schema_version, set_db_schema_version, SCHEMA_VERSION
from openprocurement.auctions.rubble.tests.base import BaseWebTest, BaseAuctionWebTest, test_bids, test_auction_data
from openprocurement.auctions.rubble.tests.blanks.migration_blanks import (
    # MigrateTestFrom1To2Bids
    migrate_one_pending,
    migrate_one_active,
    migrate_unsuccessful_active,
    migrate_unsuccessful_pending,
    # MigrateTestFrom1To2WithTwoBids
    migrate_pending_to_unsuccesful,
    migrate_pending_to_complete,
    migrate_active_to_unsuccessful,
    migrate_active_to_complete,
    migrate_cancelled_pending_to_complete,
    migrate_unsuccessful_pending_to_complete,
    migrate_unsuccessful_active_to_complete,
    migrate_cancelled_unsuccessful_pending,
    migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful,
    migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful,
    migrate_awards_number,
    # MigrateTestFrom1To2WithThreeBids
    migrate_unsuccessful_unsuccessful_pending,
    migrate_unsuccessful_unsuccessful_active,
    # MigrateDocumentOf
    migrate_document_of_auction_documents,
    migrate_document_of_bids_documents,
    migrate_document_of_awards_documents,
    migrate_document_of_contracts_documents,
    migrate_document_of_cancellations_documents
)

from openprocurement.auctions.rubble.migration import (
    RubbleMigrationsRunner, DocumentOfStep, PACKAGE_ALIASES
)
from openprocurement.api.tests.fixtures.mocks import MigrationResourcesDTO_mock


class MigrateTest(BaseWebTest):

    def setUp(self):
        super(MigrateTest, self).setUp()
        migrate_data(self.app.app.registry)

    def test_migrate(self):
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)
        migrate_data(self.app.app.registry, 1)
        self.assertEqual(get_db_schema_version(self.db), SCHEMA_VERSION)


class MigrateTestFrom1To2Bids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    test_migrate_one_pending = snitch(migrate_one_pending)
    test_migrate_one_active = snitch(migrate_one_active)
    test_migrate_unsuccessful_active = snitch(migrate_unsuccessful_active)
    test_migrate_unsuccessful_pending = snitch(migrate_unsuccessful_pending)

    def setUp(self):
        super(MigrateTestFrom1To2Bids, self).setUp()
        migrate_data(self.app.app.registry)
        set_db_schema_version(self.db, 0)
        auction = self.db.get(self.auction_id)
        auction['bids'][0]['value']['amount'] = auction['value']['amount']
        self.db.save(auction)


class MigrateTestFrom1To2WithTwoBids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    test_migrate_pending_to_unsuccesful = snitch(migrate_pending_to_unsuccesful)
    test_migrate_pending_to_complete = snitch(migrate_pending_to_complete)
    test_migrate_active_to_unsuccessful= snitch(migrate_active_to_unsuccessful)
    test_migrate_active_to_complete = snitch(migrate_active_to_complete)
    test_migrate_cancelled_pending_to_complete = snitch(migrate_cancelled_pending_to_complete)
    test_migrate_unsuccessful_pending_to_complete = snitch(migrate_unsuccessful_pending_to_complete)
    test_migrate_unsuccessful_active_to_complete = snitch(migrate_unsuccessful_active_to_complete)
    test_migrate_cancelled_unsuccessful_pending = snitch(migrate_cancelled_unsuccessful_pending)
    test_migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_pending_to_unsuccessful)
    test_migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful = snitch(migrate_cancelled_unsuccessful_cancelled_active_to_unsuccessful)
    test_migrate_awards_number = snitch(migrate_awards_number)

    def setUp(self):
        super(MigrateTestFrom1To2WithTwoBids, self).setUp()
        migrate_data(self.app.app.registry)
        set_db_schema_version(self.db, 0)


class MigrateTestFrom1To2WithThreeBids(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    test_migrate_unsuccessful_unsuccessful_pending = snitch(migrate_unsuccessful_unsuccessful_pending)
    test_migrate_unsuccessful_unsuccessful_active = snitch(migrate_unsuccessful_unsuccessful_active)

    def setUp(self):
        super(MigrateTestFrom1To2WithThreeBids, self).setUp()
        migrate_data(self.app.app.registry)
        set_db_schema_version(self.db, 0)
        auction = self.db.get(self.auction_id)
        auction['bids'].append(deepcopy(auction['bids'][0]))
        auction['bids'][-1]['id'] = uuid4().hex
        self.db.save(auction)


class MigrateTestDocumentOf(BaseAuctionWebTest):
    initial_data = test_auction_data
    initial_bids = test_bids
    test_document_data = {
        'title': 'auction_protocol.pdf',
        'hash': 'md5:' + '0' * 32,
        'format': 'application/msword',
        "description": "auction protocol",
        "documentType": 'auctionProtocol',
        'url': 'http://localhost/test',
        'documentOf': 'tender'

    }
    test_migrate_document_of_auction_documents = snitch(migrate_document_of_auction_documents)
    test_migrate_document_of_bids_documents = snitch(migrate_document_of_bids_documents)
    test_migrate_document_of_awards_documents = snitch(migrate_document_of_awards_documents)
    test_migrate_document_of_contracts_documents = snitch(migrate_document_of_contracts_documents)
    test_migrate_document_of_cancellations_documents = snitch(migrate_document_of_cancellations_documents)

    def setUp(self):
        super(MigrateTestDocumentOf, self).setUp()
        self.runner = RubbleMigrationsRunner(
            MigrationResourcesDTO_mock(
                self.db, PACKAGE_ALIASES
            )
        )
        self.steps = (DocumentOfStep, )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2Bids))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2WithTwoBids))
    suite.addTest(unittest.makeSuite(MigrateTestFrom1To2WithThreeBids))
    suite.addTest(unittest.makeSuiter(MigrateTestDocumentOf))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')