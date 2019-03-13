# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    validate_with,
)
from openprocurement.auctions.core.adapters import (
    AuctionConfigurator,
    AuctionManagerAdapter
)
from openprocurement.auctions.rubble.models import (
    RubbleOther,
    RubbleFinancial
)
from openprocurement.auctions.core.plugins.awarding.v2_1.adapters import (
    AwardingV2_1ConfiguratorMixin
)
from openprocurement.auctions.rubble.validation import (
    validate_rectification_period_utcoffset,
)


class AuctionRubbleOtherConfigurator(AuctionConfigurator,
                                     AwardingV2_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleOther


class AuctionRubbleFinancialConfigurator(AuctionConfigurator,
                                         AwardingV2_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleFinancial


class AuctionRubbleOtherManagerAdapter(AuctionManagerAdapter):

    create_validators = (
        validate_rectification_period_utcoffset,
    )

    @validate_with(create_validators)
    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass


class AuctionRubbleFinancialManagerAdapter(AuctionManagerAdapter):

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass
