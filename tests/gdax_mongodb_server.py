#!/usr/bin/env python3

from pymongo import MongoClient
from trader import gdax
import time
import sys

class MyWSClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["LTC-USD", "BTC-USD", "LTC-BTC", "ETH-BTC"]

    def on_message(self, msg):
        if 'type' in msg and (msg['type'] == 'match'):
            if 'product_id' in msg and msg['product_id'] == 'LTC-USD':
                del msg['taker_order_id']
                del msg['maker_order_id']
                del msg['trade_id']
                del msg['sequence']
                count = self.db.LTCUSD.count({ "time": msg["time"]})
                if count == 0:
                    #print(msg)
                    msg['count'] = 1
                    self.db.LTCUSD.insert_one(msg)
                else:
                    self.db.LTCUSD.update({ "time": msg["time"]}, {"$inc": {"count": 1}})
            if 'product_id' in msg and msg['product_id'] == 'LTC-BTC':
                del msg['taker_order_id']
                del msg['maker_order_id']
                del msg['trade_id']
                del msg['sequence']
                count = self.db.LTCUSD.count({ "time": msg["time"]})
                if count == 0:
                    #print(msg)
                    msg['count'] = 1
                    self.db.LTCBTC.insert_one(msg)
                else:
                    self.db.LTCBTC.update({ "time": msg["time"]}, {"$inc": {"count": 1}})
            if 'product_id' in msg and msg['product_id'] == 'ETH-BTC':
                del msg['taker_order_id']
                del msg['maker_order_id']
                del msg['trade_id']
                del msg['sequence']
                count = self.db.LTCUSD.count({ "time": msg["time"]})
                if count == 0:
                    #print(msg)
                    msg['count'] = 1
                    self.db.ETHBTC.insert_one(msg)
                else:
                    self.db.ETHBTC.update({ "time": msg["time"]}, {"$inc": {"count": 1}})
            elif 'product_id' in msg and msg['product_id'] == 'BTC-USD':
                del msg['taker_order_id']
                del msg['maker_order_id']
                del msg['trade_id']
                del msg['sequence']
                count = self.db.BTCUSD.count({ "time": msg["time"]})
                if count == 0:
                    msg['count'] = 1
                    print(msg)
                    self.db.BTCUSD.insert_one(msg)
                else:
                    self.db.BTCUSD.update({ "time": msg["time"]}, {"$inc": {"count": 1}})

    def on_close(self):
        print("-- Goodbye! --")

if __name__ == '__main__':
    pc = gdax.PublicClient()
    print(pc.get_product_24hr_stats('LTC-USD'))

    while 1:
        mongo_client = MongoClient('mongodb://localhost:27017/')
        db = mongo_client.cryptocurrency_database
        ws = MyWSClient(should_print=False)
        ws.db = db
        mongo_client.drop_database('cryptocurrency_database')

        try:
            ws.start()
            print("Server started")
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            ws.close()
            sys.exit(0)
        except Exception as e:
            print('Error occurred: {}'.format(e))
            ws.close()
            print("Connection closed, restarting...")
            time.sleep(2)


