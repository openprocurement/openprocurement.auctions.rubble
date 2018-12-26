# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    context_unpack,
    json_view,
    apply_patch,
    opresource,
    save_auction,
    generate_rectificationPeriod_tender_period_margin,
)
from openprocurement.auctions.core.validation import (
    validate_patch_auction_data,
)
from openprocurement.auctions.core.views.mixins import AuctionResource
from openprocurement.auctions.core.interfaces import IAuctionManager

from openprocurement.auctions.rubble.utils import (
    check_status,
    invalidate_bids_data,
)
from openprocurement.auctions.rubble.validation import (
    validate_rectification_period_editing,
)


@opresource(name='rubbleOther:Auction',
            path='/auctions/{auction_id}',
            auctionsprocurementMethodType="rubbleOther",
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#auction for more info")
class AuctionResource(AuctionResource):

    @json_view(content_type="application/json", validators=(validate_patch_auction_data, validate_rectification_period_editing), permission='edit_auction')
    def patch(self):
        self.request.registry.getAdapter(self.context, IAuctionManager).change_auction(self.request)
        auction = self.context
        if self.request.authenticated_role != 'Administrator' and auction.status in ['complete', 'unsuccessful', 'cancelled']:
            self.request.errors.add('body', 'data', 'Can\'t update auction in current ({}) status'.format(auction.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'chronograph':
            apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
            check_status(self.request)
            save_auction(self.request)
        else:
            apply_patch(self.request, save=False, src=self.request.validated['auction_src'])
            if auction.status == 'active.tendering' and self.request.authenticated_role == 'auction_owner':
                if not auction.rectificationPeriod:
                    auction.rectificationPeriod = generate_rectificationPeriod_tender_period_margin(auction)
                invalidate_bids_data(auction)
            save_auction(self.request)
        self.LOGGER.info('Updated auction {}'.format(auction.id),
                    extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_patch'}))
        return {'data': auction.serialize(auction.status)}
