# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import (
    AuctionConfigurator,
    AuctionManagerAdapter
)
from openprocurement.auctions.rubble.models import (
    RubbleOther,
    RubbleFinancial
)
from openprocurement.auctions.core.plugins.awarding.v3_1.adapters import (
    AwardingV3_1ConfiguratorMixin
)
from openprocurement.auctions.core.plugins.contracting.v3_1.adapters import (
    ContractingV3_1ConfiguratorMixin
)


class AuctionRubbleOtherConfigurator(AuctionConfigurator,
                                     AwardingV3_1ConfiguratorMixin,
                                     ContractingV3_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleOther
    pending_admission_for_one_bid = False
    is_contract_signed_required = True


class AuctionRubbleFinancialConfigurator(AuctionConfigurator,
                                         AwardingV3_1ConfiguratorMixin,
                                         ContractingV3_1ConfiguratorMixin):
    name = 'Auction Rubble Configurator'
    model = RubbleFinancial
    pending_admission_for_one_bid = False
    is_contract_signed_required = True

class AuctionRubbleOtherManagerAdapter(AuctionManagerAdapter):

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass


class AuctionRubbleFinancialManagerAdapter(AuctionManagerAdapter):

    def create_auction(self, request):
        pass

    def change_auction(self, request):
        pass
