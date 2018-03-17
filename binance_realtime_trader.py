#!/usr/bin/python

from trader.account.binance.websockets import BinanceSocketManager
from trader.account.binance.client import Client
from trader.AccountBinance import AccountBinance
from trader.strategy import select_strategy

from config import *

class BinanceTrader:
    def __init__(self):
        self.client = Client(MY_API_KEY, MY_API_SECRET)
        self.accnt = AccountBinance(self.client, 'BNB', 'BTC')
        self.trader = select_strategy('trailing_prices_strategy', self.client, 'BTC', 'USD',
                                      account_handler=self.accnt, order_handler=None) #self.order_handler)

        self.order_handler = self.trader.order_handler
        print(self.accnt)
        self.accnt.get_account_balance()

    def process_message(self, msg):
        if 'p' in msg:
            print(msg)
            price = float(msg["p"])
            self.trader.run_update_price(price)

    def run(self):
        bm = BinanceSocketManager(self.client)
        bm.start_aggtrade_socket(self.accnt.ticker_id, self.process_message)
        bm.start()

if __name__ == '__main__':
    #print(get_products_by_volume(client))
    bt = BinanceTrader()
    bt.run()



