#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

#from pymongo import MongoClient
from trader.account.cobinhood.cobinhood.ws import feed
from trader.account.cobinhood.cobinhood.ws.response import Trade
from trader.account.cobinhood.cobinhood.configuration import Config
from trader.account.cobinhood.cobinhood.http import wallet

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