# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    TZ,
    error_handler,
    generate_rectificationPeriod_tender_period_margin,
    get_now,
    utcoffset_difference,
)


def validate_rectification_period_editing(request, **kwargs):
    if (
        request.context.status == 'active.tendering'
        and request.authenticated_role
        not in ['chronograph', 'Administrator']
    ):
        auction = request.validated['auction']
        rectificationPeriod = auction.rectificationPeriod or generate_rectificationPeriod_tender_period_margin(auction)
        if rectificationPeriod.endDate.astimezone(TZ) < get_now():
            request.errors.add(
                'body',
                'data',
                'Auction can be edited only during the rectification period: from ({}) to ({}).'.format(
                    rectificationPeriod.startDate.isoformat(),
                    rectificationPeriod.endDate.isoformat()
                )
            )
            request.errors.status = 403
            raise error_handler(request)


def validate_rectification_period_utcoffset(request, **kwargs):
    rp = request.validated['auction']['rectificationPeriod']
    if not rp:
        return
    rp_end_date = request.validated['auction']['rectificationPeriod']['endDate']
    if not rp_end_date:
        return
    offset_difference, server_offset_value = utcoffset_difference(rp_end_date)
    if offset_difference != 0:
        request.errors.add(
            'body',
            'data',
            'utcoffset of rectificationPeriod.endDate should be equal to 0{0}:00'.format(
                server_offset_value,
            )
        )
        request.errors.status = 422
        raise error_handler(request)
