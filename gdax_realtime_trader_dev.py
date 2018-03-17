#!/usr/bin/python

#from pymongo import MongoClient
import time
import trader.account.gdax as gdax
from trader.account.gdax.authenticated_client import AuthenticatedClient
from trader.AccountGDAX import AccountGDAX
import threading
import sys
from trader.WebHandler import WebThread
from trader.strategy import *
from trader.StrategyHandler import StrategyHandler

from config import *

# {u'product_id': u'LTC-USD', u'remaining_size': u'6.00000000', u'sequence': 1607580372, u'order_id': u'f2111bfa-2d77-47b7-b863-6ddcd548e53c', u'price': u'213.49000000', u'reason': u'canceled', u'time': u'2018-02-16T10:55:55.497000Z', u'type': u'done', u'side': u'sell'}
# {u'product_id': u'LTC-USD', u'sequence': 1607589271, u'taker_order_id': u'46cf1c41-e6e6-4c10-92df-b9a4073b9a18', u'price': u'212.90000000', u'trade_id': 25902403, u'time': u'2018-02-16T10:59:30.774000Z', u'maker_order_id': u'b75d5a95-0e47-49a1-a567-d0ca4310be9f', u'type': u'match', u'side': u'buy', u'size': u'0.56921202'}

class MyWSClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        #self.products = ["BTC-USD"]
        self.channels = ["full", "level2"]

        #self.auth_client = gdax.AuthenticatedClient(GDAX_KEY_SB, GDAX_SECRET_SB, GDAX_PASS_SB,
        #                                       api_url="https://api-public.sandbox.gdax.com")
        self.auth_client = AuthenticatedClient(GDAX_KEY, GDAX_SECRET, GDAX_PASS)
        self.accnt = AccountGDAX(self.auth_client, 'BTC', 'USD', simulation=True)
        print(self.accnt.get_account_balance())

        self.trader = StrategyHandler('trailing_prices_strategy', self.auth_client, 'BTC', 'USD',
                                      account_handler=self.accnt, order_handler=None) #self.order_handler)

        self.order_handler = self.trader.order_handler
        self.products = [self.trader.get_ticker_id()]
        #self.stat_timer = Timer(20 * 60, self.get_stats())
        self.interval_price = 0.0

        # start Web API
        thread = threading.Thread(target=WebThread, args=(self.trader,))
        thread.daemon = True
        thread.start()

    def get_stats(self):
        self.order_handler.print_stats()

    def on_message(self, msg):
        if 'bids' in msg or 'asks' in msg or 'changes' in msg:
            self.trader.run_update_orderbook(msg)
        elif 'type' in msg and 'match' in msg['type']:
            if 'price' in msg:
                self.interval_price = msg['price']
                if self.trader.strategy_name != 'quadratic_with_fibonacci':
                    self.trader.run_update_price(msg)
            #self.trader.run_update_price(msg)
        #else:
        #    print(msg)

    def on_close(self):
        #self.trader.close()
        print("closing...")
        sys.exit(0)

def compute_sum(values):
    if len(values) == 0: return 0
    total = 0.0
    for value in values:
        total += value
    return total / len(values)

def WebMain(trader=None):
    try:
        thread = threading.Thread(target=WebThread, args=[trader])
        thread.daemon = True
        thread.start()
        while thread.isAlive():
            thread.join(1)  # not sure if there is an appreciable cost to this.
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'
        sys.exit()

if __name__ == '__main__':
        ws = MyWSClient(should_print=False)
        last_price = 0.0
        counter = 0
        #try:
        if 1:
            ws.start()
            print("Started")
            while 1:
                if ws.trader.strategy_name == 'quadratic_with_fibonacci':
                    ws.trader.interval_price = ws.interval_price
                    if ws.interval_price != 0.0 and ws.interval_price != last_price:
                        msg = {'type': 'match', 'price': ws.interval_price, 'time': 0}
                        ws.trader.run_update_price(msg)
                        last_price = ws.interval_price
                time.sleep(1)
                counter += 1
                if counter >= 60:
                    counter = 0
                    ws.accnt.update_24hr_stats()
                #ws.stat_timer.start()
                #ws.stat_timer.join()
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            ws.trader.close()
            ws.close()
            sys.exit(0)
        except Exception as e:
            print('Error occurred: {}'.format(e))
            ws.close()
            print("Connection closed, restarting...")
            time.sleep(2)
