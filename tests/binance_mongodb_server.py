#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

from pymongo import MongoClient
from trader.account.binance.client import Client
from trader.account.binance.websockets import BinanceSocketManager
import time
import sys

from trader.config import *

#def process_message(msg):
#    print("message type: {}".format(msg['e']))
#    print(msg)

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    prices = client.get_all_tickers()

    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client.cryptocurrency_database
    mongo_collection = db.XRP_collection

    while 1:
        try:
            def process_message(msg):
                if mongo_collection:
                    mongo_collection.insert_one(msg)                    
                print("message type: {}".format(msg['e']))
                print(msg)

            bm = BinanceSocketManager(client)
            bm.start_aggtrade_socket('XRPBTC', process_message)
            bm.start()
            print("Server started")
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            bm.close()
            sys.exit(0)
        except:
            bm.close()
            print("Connection closed, restarting...")
            time.sleep(2)

