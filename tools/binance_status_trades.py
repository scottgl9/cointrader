#!/usr/bin/python
# get current percent loss/profit of open trades from trade.db

import sys
import os
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.AccountBinance import AccountBinance
from trader.account.binance import client
from trader.lib.TraderDB import TraderDB
from trader.config import *

if __name__ == '__main__':
    client = client.Client(MY_API_KEY, MY_API_SECRET)

    if not os.path.exists('trade.db'):
        print("trade.db doesn't exist, exiting")
        sys.exit(-1)

    accnt = AccountBinance(client)
    traderdb = TraderDB(filename='trade.db')
    traderdb.connect()
    trades = traderdb.get_all_trades()
    traderdb.close()

    tickers = client.get_all_tickers()

    for trade in trades:
        symbol = trade['symbol']
        buy_price = float(trade['price'])
        buy_size = float(trade['size'])
        try:
            price = float(tickers[symbol])
        except KeyError:
            continue

        pchange = round(100.0 * (price - buy_price) / buy_price, 2)
        print("{}: {}%".format(symbol, pchange))
