# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta

from openprocurement.auctions.core.tests.contract import (
    AuctionContractDocumentResourceTestMixin,
    AuctionContractResourceTestMixin,
    Auction2LotContractDocumentResourceTestMixin
)

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.plugins.contracting.v3_1.tests.contract import (
    AuctionContractV3_1ResourceTestCaseMixin
)
from openprocurement.auctions.core.utils import (
    get_now,
    get_related_award_of_contract
)


from openprocurement.auctions.rubble.tests.blanks.contract_blanks import (
    patch_auction_contract_to_active
)

from openprocurement.auctions.rubble.tests.base import BaseAuctionWebTest, test_auction_data, test_bids, test_lots, test_financial_auction_data, test_financial_bids, test_financial_organization




DOCUMENTS = {
    'contract': {
        'name': 'contract_signed.pdf',
        'type': 'contractSigned',
        'description': 'contract signed'
    },
    'rejection': {
        'name': 'rejection_protocol.pdf',
        'type': 'rejectionProtocol',
        'description': 'rejection protocol'
    },
    'act': {
        'name': 'act.pdf',
        'type': 'act',
        'description': 'act'
    }
}


class AuctionContractResourceTest(BaseAuctionWebTest, AuctionContractResourceTestMixin, AuctionContractV3_1ResourceTestCaseMixin):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids

    test_patch_auction_contract_to_active = snitch(patch_auction_contract_to_active)

    def setUp(self):
        super(AuctionContractResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": b['value']
                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.app.authorization = authorization
        self.award = auction['awards'][0]
        self.award_id = self.award['id']
        self.award_value = self.award['value']
        self.award_suppliers = self.award['suppliers']

        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'auction_owner')

        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token
        ), {"data": {"status": "pending"}})
        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token
        ), {"data": {"status": "active"}})
        response = self.app.get('/auctions/{}'.format(self.auction_id))
        auction = response.json['data']
        self.award_contract_id = auction['contracts'][0]['id']



    def upload_contract_document(self, contract, doc_type):
        # Uploading contract document
        response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(
            self.auction_id, contract['id'], self.auction_token
        ), upload_files=[
            ('file', DOCUMENTS[doc_type]['name'], 'content')
        ])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(
            DOCUMENTS[doc_type]['name'], response.json["data"]["title"]
        )

        # Patching it's documentType to needed one
        response = self.app.patch_json(
            '/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(
                self.auction_id, contract['id'], doc_id, self.auction_token
            ),
            {"data": {
                "description": DOCUMENTS[doc_type]['description'],
                "documentType": DOCUMENTS[doc_type]['type']
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(
            response.json["data"]["documentType"], DOCUMENTS[doc_type]['type']
        )

    def check_related_award_status(self, contract, status):
        # Checking related award status
        response = self.app.get('/auctions/{}/awards'.format(self.auction_id))
        contract = self.app.get('/auctions/{}/contracts/{}'.format(
            self.auction_id, contract['id']
        )).json['data']

        award = get_related_award_of_contract(
            contract, {'awards': response.json['data']}
        )

        response = self.app.get('/auctions/{}/awards/{}'.format(
            self.auction_id, award['id']
        ))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["status"], status)





class AuctionContractDocumentResourceTest(BaseAuctionWebTest, AuctionContractResourceTestMixin, AuctionContractV3_1ResourceTestCaseMixin):
    #initial_data = auction_data
    initial_status = 'active.auction'
    initial_bids = test_bids
    docservice = True

    def setUp(self):
        super(AuctionContractDocumentResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": b['value']
                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        self.app.authorization = authorization
        self.award = auction['awards'][0]
        self.award_id = self.award['id']
        self.award_value = self.award['value']
        self.award_suppliers = self.award['suppliers']

        response = self.app.post('/auctions/{}/awards/{}/documents?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token), upload_files=[('file', 'auction_protocol.pdf', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/auctions/{}/awards/{}/documents/{}?acc_token={}'.format(self.auction_id, self.award_id, doc_id, self.auction_token), {"data": {
            "description": "auction protocol",
            "documentType": 'auctionProtocol'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["documentType"], 'auctionProtocol')
        self.assertEqual(response.json["data"]["author"], 'auction_owner')

        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token
        ), {"data": {"status": "pending"}})
        self.app.patch_json('/auctions/{}/awards/{}?acc_token={}'.format(
            self.auction_id, self.award_id, self.auction_token
        ), {"data": {"status": "active"}})
        # Assure contract for award is created
        response = self.app.get('/auctions/{}/contracts'.format(self.auction_id))
        contract = response.json['data'][0]
        self.contract_id = contract['id']
        response = self.app.get('/auctions/{}'.format(self.auction_id))
        auction = response.json['data']
        self.award_contract_id = auction['contracts'][0]['id']



    def upload_contract_document(self, contract, doc_type):
        # Uploading contract document
        response = self.app.post('/auctions/{}/contracts/{}/documents?acc_token={}'.format(
            self.auction_id, contract['id'], self.auction_token
        ), upload_files=[
            ('file', DOCUMENTS[doc_type]['name'], 'content')
        ])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(
            DOCUMENTS[doc_type]['name'], response.json["data"]["title"]
        )

        # Patching it's documentType to needed one
        response = self.app.patch_json(
            '/auctions/{}/contracts/{}/documents/{}?acc_token={}'.format(
                self.auction_id, contract['id'], doc_id, self.auction_token
            ),
            {"data": {
                "description": DOCUMENTS[doc_type]['description'],
                "documentType": DOCUMENTS[doc_type]['type']
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(
            response.json["data"]["documentType"], DOCUMENTS[doc_type]['type']
        )

    def check_related_award_status(self, contract, status):
        # Checking related award status
        response = self.app.get('/auctions/{}/awards'.format(self.auction_id))
        contract = self.app.get('/auctions/{}/contracts/{}'.format(
            self.auction_id, contract['id']
        )).json['data']

        award = get_related_award_of_contract(
            contract, {'awards': response.json['data']}
        )

        response = self.app.get('/auctions/{}/awards/{}'.format(
            self.auction_id, award['id']
        ))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["status"], status)




class FinancialAuctionContractResourceTest(AuctionContractResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


class FinancialAuctionContractDocumentResourceTest(AuctionContractDocumentResourceTest):
    initial_bids = test_financial_bids
    initial_data = test_financial_auction_data
    initial_organization = test_financial_organization


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuctionContractResourceTest))
    suite.addTest(unittest.makeSuite(AuctionContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionContractResourceTest))
    suite.addTest(unittest.makeSuite(FinancialAuctionContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
