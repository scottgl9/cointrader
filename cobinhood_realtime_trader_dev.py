#!/usr/bin/python

#from pymongo import MongoClient
from trader.account.cobinhood.ws import feed
from trader.account.cobinhood.ws.response import Trade
from trader.account.cobinhood.configuration import Config
from trader.account.cobinhood.http import wallet

from trader.config import *

Config.API_TOKEN = CB_KEY
print wallet.get_balances()


# sandbox:
#'web' = > 'https://sandbox-api.cobinhood.com',
#'ws' = > 'wss://sandbox-feed.cobinhood.com',



def on_message(ws_obj, msg):
    print ws_obj.exchange_data.orderbook
    print msg

ws = feed.CobinhoodWS()
#eth_orderbook = Ticker('COB-BTC')
cob_btc = Trade('COB-BTC')
ws.start(subscribe=[cob_btc], on_message=on_message)