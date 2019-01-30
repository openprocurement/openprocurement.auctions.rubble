import os
import logging
from pyramid.interfaces import IRequest

from openprocurement.auctions.core.includeme import (
    IContentConfigurator,
    IAwardingNextCheck,
    get_evenly_plugins
)
from openprocurement.auctions.core.interfaces import IAuctionManager
from openprocurement.auctions.core.plugins.awarding.vX.adapters import (
    AwardingNextCheckVX
)

from openprocurement.auctions.rubble.adapters import (
    AuctionRubbleOtherConfigurator,
    AuctionRubbleFinancialConfigurator,
    AuctionRubbleOtherManagerAdapter,
    AuctionRubbleFinancialManagerAdapter
)
from openprocurement.auctions.rubble.constants import (
    DEFAULT_LEVEL_OF_ACCREDITATION,
    DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER,
    DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
)
from openprocurement.auctions.rubble.models import (
    IRubbleOtherAuction,
    IRubbleFinancialAuction,
    RubbleOther,
    RubbleFinancial
)

LOGGER = logging.getLogger(__name__)


def includeme_other(config, plugin_map):
    procurement_method_types = plugin_map.get('aliases', [])
    if plugin_map.get('use_default', False):
        procurement_method_types.append(
            DEFAULT_PROCUREMENT_METHOD_TYPE_OTHER
        )
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(RubbleOther,
                                                 procurementMethodType)

    config.scan("openprocurement.auctions.rubble.views.other")

    # Register adapters
    config.registry.registerAdapter(
        AuctionRubbleOtherConfigurator,
        (IRubbleOtherAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckVX,
        (IRubbleOtherAuction,),
        IAwardingNextCheck
    )
    config.registry.registerAdapter(
        AuctionRubbleOtherManagerAdapter,
        (IRubbleOtherAuction,),
        IAuctionManager
    )

    LOGGER.info("Included openprocurement.auctions.rubble.other plugin",
                extra={'MESSAGE_ID': 'included_plugin'})

    # add accreditation level
    if not plugin_map.get('accreditation'):
        config.registry.accreditation['auction'][RubbleOther._internal_type] = DEFAULT_LEVEL_OF_ACCREDITATION
    else:
        config.registry.accreditation['auction'][RubbleOther._internal_type] = plugin_map['accreditation']

    # migrate data
    if plugin_map['migration'] and not os.environ.get('MIGRATION_SKIP'):
        get_evenly_plugins(config, plugin_map['plugins'], 'openprocurement.auctions.rubble.plugins')


def includeme_financial(config, plugin_map):
    procurement_method_types = plugin_map.get('aliases', [])
    if plugin_map.get('use_default', False):
        procurement_method_types.append(
            DEFAULT_PROCUREMENT_METHOD_TYPE_FINANCIAL
        )
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(RubbleFinancial,
                                                 procurementMethodType)

    config.scan("openprocurement.auctions.rubble.views.financial")

    # Register Adapters
    config.registry.registerAdapter(
        AuctionRubbleFinancialConfigurator,
        (IRubbleFinancialAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AwardingNextCheckVX,
        (IRubbleFinancialAuction,),
        IAwardingNextCheck
    )
    config.registry.registerAdapter(
        AuctionRubbleFinancialManagerAdapter,
        (IRubbleFinancialAuction,),
        IAuctionManager
    )

    LOGGER.info("Included openprocurement.auctions.rubble.financial plugin",
                extra={'MESSAGE_ID': 'included_plugin'})

    # add accreditation level
    if not plugin_map.get('accreditation'):
        config.registry.accreditation['auction'][RubbleFinancial._internal_type] = DEFAULT_LEVEL_OF_ACCREDITATION
    else:
        config.registry.accreditation['auction'][RubbleFinancial._internal_type] = plugin_map['accreditation']

    # migrate data
    if plugin_map['migration'] and not os.environ.get('MIGRATION_SKIP'):
        get_evenly_plugins(config, plugin_map['plugins'], 'openprocurement.auctions.rubble.plugins')
