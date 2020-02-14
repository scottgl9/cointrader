#!/usr/bin/python
# get current percent loss/profit of open trades from trade.db

import sys
import os
try:
    import trader
except ImportError:
    sys.path.append('.')

import argparse
from trader.account.binance.AccountBinance import AccountBinance
from trader.account.binance.binance import client
from trader.lib.TraderDB import TraderDB
from trader.config import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--db', action='store', dest='trade_db_path',
                        default='trade.db',
                        help='Path to trade.db')

    parser.add_argument('--remove', action='store', dest='remove_symbol',
                        default='',
                        help='Remove symbol entry from trade.db')

    results = parser.parse_args()

    trade_db_path = results.trade_db_path

    if not os.path.exists(trade_db_path):
        print("{} doesn't exist, exiting".format(trade_db_path))
        sys.exit(-1)

    client = client.Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client)
    traderdb = TraderDB(filename=trade_db_path)
    traderdb.connect()

    if results.remove_symbol:
        print("Removing {} from {}".format(results.remove_symbol, trade_db_path))
        traderdb.remove_trade(results.remove_symbol)

    trades = traderdb.get_all_trades()
    traderdb.close()

    tickers = {}
    for ticker in client.get_all_tickers():
        symbol = ticker['symbol']
        price = float(ticker['price'])
        tickers[symbol] = price

    for trade in trades:
        symbol = trade['symbol']
        buy_price = float(trade['price'])
        #buy_size = float(trade['size'])
        try:
            price = float(tickers[symbol])
        except KeyError:
            continue

        pchange = round(100.0 * (price - buy_price) / buy_price, 2)
        print("{}: {}%".format(symbol, pchange))
