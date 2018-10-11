#!/usr/bin/env python3
'''pyetrade market unit tests
   TODO:
       * lint'''

import string
import random
import unittest
import datetime as dt
from unittest.mock import patch
from pyetrade import market

global option_response
option_response = {'2018-10': {'all': {'adjNonAdjFlag': False,
                      'annualDividend': 0,
                      'ask': 0.01,
                      'askExchange': 'N',
                      'askSize': 16,
                      'askTime': '16:00:00 EDT 05-16-2018',
                      'bid': 0,
                      'bidExchange': 'Q',
                      'bidSize': 0,
                      'bidTime': '16:00:00 EDT 05-16-2018',
                      'chgClose': 0,
                      'chgClosePrcn': 0,
                      'companyName': '',
                      'daysToExpiration': 157,
                      'dirLast': 'U',
                      'dividend': 0,
                      'eps': 0,
                      'estEarnings': 0,
                      'exDivDate': '',
                      'exchgLastTrade': '',
                      'fsi': ' ',
                      'high': 0.02,
                      'high52': 0.02,
                      'highAsk': 5,
                      'highBid': 0,
                      'lastTrade': 0.02,
                      'low': 0.02,
                      'low52': 0.02,
                      'lowAsk': 0.01,
                      'lowBid': 0,
                      'numTrades': 0,
                      'open': 0,
                      'openInterest': 1,
                      'optionStyle': 'A',
                      'optionUnderlier': 'AAPL',
                      'prevClose': 0.02,
                      'prevDayVolume': 0,
                      'primaryExchange': 'Z ',
                      'symbolDesc': "AAPL Oct 19 '18 $2.50 Put",
                      'todayClose': 0,
                      'totalVolume': 0,
                      'upc': 0,
                      'volume10Day': 0},
                     'dateTime': '03:00:00 EDT 04-06-2018',
                     'product': {'exchange': 'Z ',
                      'expirationDay': 19,
                      'expirationMonth': 10,
                      'expirationYear': 2018,
                      'optionType': 'PUT',
                      'strikePrice': '2.500',
                      'symbol': 'AAPL',
                      'type': 'OPTN' }}}

class TestETradeMarket(unittest.TestCase):
    '''TestEtradeMarket Unit Test'''
    # Mock out OAuth1Session
    @patch('pyetrade.market.OAuth1Session')
    def test_look_up_product(self, MockOAuthSession):
        '''test_look_up_product(MockOAuthSession) -> None
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        # Set Mock returns
        MockOAuthSession().get().json.return_value = "{'BAC': '32.10'}"
        MockOAuthSession().get().text = r'<xml> returns </xml>'
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        # Test Get Quote JSON
        self.assertEqual(mark.look_up_product('Bank Of', 'EQ'), "{'BAC': '32.10'}" )
        self.assertTrue(MockOAuthSession().get().json.called)
        self.assertTrue(MockOAuthSession().get.called)
        # Test Get Qoute xml
        self.assertEqual(mark.look_up_product('Back Of', 'EQ', resp_format='xml'), r"<xml> returns </xml>")
        self.assertTrue(MockOAuthSession().get.called)
        
    # Mock out OAuth1Session
    @patch('pyetrade.market.OAuth1Session')
    def test_get_quote(self, MockOAuthSession):
        '''test_get_quote(MockOAuthSession) -> None
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        # Set Mock returns
        MockOAuthSession().get().json.return_value = "{'BAC': '32.10'}"
        MockOAuthSession().get().text = r'<xml> returns </xml>'
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        # Test prod Get Qoute
        self.assertEqual(mark.get_quote('BAC'), "{'BAC': '32.10'}")
        self.assertTrue(MockOAuthSession().get().json.called)
        self.assertTrue(MockOAuthSession().get.called)
        # Test prod Get Qoute xml
        self.assertEqual(mark.get_quote('BAC', resp_format='xml'), r"<xml> returns </xml>")
        self.assertTrue(MockOAuthSession().get.called)
        
        # Test log message if more than 25 quotes are requested
        # Generate 30 symbols; response should only be 25 symbols
        sym = [''.join(random.choice(string.ascii_uppercase) for _ in range(3)) for _ in range(30)]
        retn = {x:32.1 for x in sym[:25]}
        retn_str = str(retn)
        MockOAuthSession().get().json.return_value = retn_str
        self.assertEqual(mark.get_quote(sym), retn_str)
        self.assertTrue(MockOAuthSession().get().json.called)
        self.assertTrue(MockOAuthSession().get.called)

    @patch('pyetrade.market.OAuth1Session')
    def test_get_quote_exception(self, MockOAuthSession):
        '''test_get_quote(MockOAuthSession) -> None
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        # Generate symbols
        sym = [''.join(random.choice(string.ascii_uppercase) for _ in range(3)) for _ in range(25)]
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)

        # Test exception class
        mark.get_quote(sym)

    @patch('pyetrade.market.OAuth1Session')
    def test_get_all_option_data(self, MockOAuthSession):
        '''test_get_all_option_data(MockOAuthSession)
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        sym = 'AAPL'
        MockOAuthSession().get().return_value = option_response
        self.assertEqual(mark.get_all_option_data(sym), option_response)
        self.assertTrue(MockOAuthSession().get.called)
        
    @patch('pyetrade.market.OAuth1Session')
    def test_get_option_chain_data(self, MockOAuthSession):
        '''test_get_option_chain_data(MockOAuthSession)
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        sym = 'AAPL'
        date_strikes = { 'put':  [ (dt.date(2018,10,19),2.5) ],
                         'call': [ (dt.date(2018,10,19),2.5) ]
                        }
        MockOAuthSession().get().return_value = option_response
        self.assertEqual(mark.get_option_chain_data(sym,date_strikes), option_response)
        self.assertTrue(MockOAuthSession().get.called)
        
    @patch('pyetrade.market.OAuth1Session')
    def test_get_option_strikes(self, MockOAuthSession):
        '''test_get_option_strikes(MockOAuthSession)
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        sym = 'AAPL'
        response = { 'put':  [ (dt.date(2018,10,19),100.0), (dt.date(2018,10,19),200.0) ],
                     'call': [ (dt.date(2018,10,19),100.0), (dt.date(2018,10,19),200.0) ]
                     }
        MockOAuthSession().get().return_value = response
        self.assertEqual(mark.get_option_strikes(sym,10,2018), response)
        self.assertTrue(MockOAuthSession().get.called)
        
    # Mock out OAuth1Session
    @patch('pyetrade.market.OAuth1Session')
    def test_get_optionchains(self, MockOAuthSession):
        '''test_get_optionchains(MockOAuthSession) -> None
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        # Set Mock returns
        MockOAuthSession().get().json.return_value = str(option_response)
        MockOAuthSession().get().text = r'<xml> returns </xml>'
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        
        # Test prod Get Qoute
        self.assertEqual(mark.get_optionchains('AAPL', 10, 2018, skipAdjusted=True, chainType='callput', resp_format='json'), str(option_response))
        self.assertTrue(MockOAuthSession().get().json.called)
        self.assertTrue(MockOAuthSession().get.called)
        # Test prod Get Qoute xml
        self.assertEqual(mark.get_optionchains('AAPL', resp_format='xml'), r"<xml> returns </xml>")
        self.assertTrue(MockOAuthSession().get.called)
        
    # Mock out OAuth1Session
    @patch('pyetrade.market.OAuth1Session')
    def test_get_optionexpiredate(self, MockOAuthSession):
        '''test_get_optionexpiredate(MockOAuthSession) -> None
           param: MockOAuthSession
           type: mock.MagicMock
           description: MagicMock of OAuth1Session'''
        # Set Mock returns
        MockOAuthSession().get().return_value = [ dt.date(2018,10,19) ]
        mark = market.ETradeMarket('abc123', 'xyz123', 'abctoken', 'xyzsecret', dev=False)
        self.assertEqual(mark.get_optionexpiredate('AAPL'), [ dt.date(2018,10,19) ])
        self.assertTrue(MockOAuthSession().get.called)
        