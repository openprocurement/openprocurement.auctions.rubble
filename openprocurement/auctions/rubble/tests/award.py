# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy


from openprocurement.auctions.rubble.tests.base import (
    BaseAuctionWebTest, test_lots, test_organization,
    test_bids as base_bids,
    test_financial_auction_data,
    test_financial_organization,
)
from openprocurement.auctions.core.tests.base import snitch

from openprocurement.auctions.core.tests.award import (
    AuctionAwardDocumentResourceTestMixin
)
from openprocurement.auctions.core.tests.plugins.awarding.vX.tests.award import (
    AuctionAwardProcessTestMixin,
    CreateAuctionAwardTestMixin

)
from openprocurement.auctions.core.utils import get_now, get_related_contract_of_award


bid = {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 459,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        },
        "qualified": True
       }
test_bids = deepcopy(base_bids)
test_bids.append(bid)

test_financial_bids = []
for i in test_bids:
    bid = deepcopy(i)
    bid.update({'eligible': True})
    bid['tenderers'] = [test_financial_organization]
    test_financial_bids.append(bid)


@unittest.skip("option not available")
class CreateAuctionAwardTest(BaseAuctionWebTest, CreateAuctionAwardTestMixin):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_bids = test_bids
    docservice = True


class AuctionAwardProcessTest(BaseAuctionWebTest, AuctionAwardProcessTestMixin):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids
    docservice = True

    def upload_rejection_protocol(self, award):
        owner_token = self.auction_token
        award_id = award['id']

        response = self.app.post(
            '/auctions/{}/awards/{}/documents?acc_token={}'.format(
                self.auction_id, award_id, owner_token
            ), upload_files=[('file', 'rejection_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(
            'rejection_protocol.pdf', response.json["data"]["title"]
        )

        response = self.app.patch_json(
            '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(
                self.auction_id, award_id, doc_id, owner_token
            ),
            {"data": {
                "description": "rejection protocol",
                "documentType": 'rejectionProtocol'
            }})

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(
            response.json["data"]["documentType"], 'rejectionProtocol'
        )

    def set_award_unsuccessful(self, award):
        response = self.app.get(
            '/auctions/{}/contracts'.format(self.auction_id)
        )

        contract = get_related_contract_of_award(
            award['id'], {'contracts': response.json['data']}
        )

        response = self.app.post(
            '/auctions/{}/contracts/{}/documents?acc_token={}'.format(
                self.auction_id, contract['id'], self.auction_token
            ), upload_files=[('file', 'rejection_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']

        response = self.app.patch_json(
            '/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(
                self.auction_id, contract['id'], doc_id, self.auction_token
            ),
            {"data": {
                "description": "rejection protocol",
                "documentType": 'rejectionProtocol'
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json(
            '/auctions/{}/contracts/{}?acc_token={}'.format(
                self.auction_id, contract['id'], self.auction_token
            ), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        response = self.app.get('/auctions/{}/awards/{}'.format(
            self.auction_id, award['id']
        ))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def upload_auction_protocol(self, award):
        award_id = award['id']
        bid_token = self.initial_bids_tokens[award['bid_id']]
        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, bid_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, bid_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('auction_protocol.pdf', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.patch_json(
            '/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, award_id, doc_id, self.auction_token),
            {"data": {
                "description": "auction protocol",
                "documentType": 'auctionProtocol'
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')

        response = self.app.get('/auctions/{}/awards/{}/documents'.format(self.auction_id,award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual('auctionProtocol', response.json["data"][0]["documentType"])
        self.assertEqual('auction_protocol.pdf', response.json["data"][0]["title"])
        self.assertEqual('bid_owner', response.json["data"][0]["author"])
        self.assertEqual('auctionProtocol', response.json["data"][1]["documentType"])
        self.assertEqual('auction_owner', response.json["data"][1]["author"])



    def setUp(self):
        super(AuctionAwardProcessTest, self).setUp()
        self.post_auction_results()


@unittest.skip("option not available")
class AuctionLotAwardResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids


@unittest.skip("option not available")
class Auction2LotAwardResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_lots = 2 * test_lots
    initial_bids = test_bids


@unittest.skip("option not available")
class AuctionAwardComplaintResourceTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardComplaintResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class AuctionLotAwardComplaintResourceTest(BaseAuctionWebTest):
    #initial_data = auction_data
    initial_status = 'active.qualification'
    initial_lots = test_lots
    initial_bids = test_bids

    def setUp(self):
        super(AuctionLotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


@unittest.skip("option not available")
class Auction2LotAwardComplaintResourceTest(BaseAuctionWebTest):
    initial_lots = 2 * test_lots


@unittest.skip("option not available")
class AuctionAwardComplaintDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


@unittest.skip("option not available")
class Auction2LotAwardComplaintDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/auctions/{}/awards/{}/complaints'.format(
            self.auction_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


class AuctionAwardDocumentResourceTest(BaseAuctionWebTest, AuctionAwardDocumentResourceTestMixin):
    initial_status = 'active.auction'
    initial_bids = test_bids

    def setUp(self):
        super(AuctionAwardDocumentResourceTest, self).setUp()
        self.post_auction_results()


@unittest.skip("option not available")
class Auction2LotAwardDocumentResourceTest(BaseAuctionWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Auction2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.initial_bids[0]
        response = self.app.post_json('/auctions/{}/awards'.format(
            self.auction_id), {'data': {'suppliers': [self.initial_organization], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']


class CreateFinancialAuctionAwardTest(CreateAuctionAwardTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardProcessTest(AuctionAwardProcessTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardResourceTest(AuctionLotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardResourceTest(Auction2LotAwardResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintResourceTest(AuctionAwardComplaintResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionLotAwardComplaintResourceTest(AuctionLotAwardComplaintResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintResourceTest(Auction2LotAwardComplaintResourceTest):
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuctionAwardComplaintDocumentResourceTest(AuctionAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardComplaintDocumentResourceTest(Auction2LotAwardComplaintDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionAwardDocumentResourceTest(AuctionAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


@unittest.skip("option not available")
class FinancialAuction2LotAwardDocumentResourceTest(Auction2LotAwardDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Auction2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Auction2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(AuctionAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(AuctionLotAwardResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuction2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionLotAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
