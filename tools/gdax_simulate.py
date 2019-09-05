#!/usr/bin/env python3

import os.path
import time
import sys
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from trader.strategy import *
from trader.AccountSimulate import AccountSimulate
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
import inspect

def time_difference_in_hours(ts1, ts2):
    time1 = datetime.fromtimestamp(ts1)
    time2 = datetime.fromtimestamp(ts2)
    hours, remainder = divmod((time2 - time1).total_seconds(), 3600)
    return hours

def update_24hrs(cdays, strategy):
    ts_24hr, strategy.accnt.low_24hr, strategy.accnt.high_24hr, open_24hr, close_24hr, volume_24hr = cdays.fetchone()
    return ts_24hr

def simulate(conn, strategy):
    c = conn.cursor()
    cdays = conn.cursor()
    c.execute("SELECT * FROM klines ORDER BY timestamp ASC")

    cdays.execute("SELECT * FROM klines_days ORDER BY timestamp ASC")
    ts_24hr = update_24hrs(cdays, strategy)

    first_buy_price = 0.0
    last_sell_price = 0.0
    initial_balance_usd = strategy.accnt.quote_currency_balance
    for row in c:
        timestamp, low, high, openprice, closeprice, volume = row

        if low < 1.0 or high < 1.0 or openprice < 1.0 or closeprice < 1.0: continue

        if first_buy_price == 0.0:
            first_buy_price = openprice

        last_sell_price = closeprice

        msg = {'type': 'match', 'price': openprice, 'timestamp': timestamp, 'volume': volume}
        strategy.run_update_price(msg)
        msg = {'type': 'match', 'price': closeprice, 'timestamp': timestamp, 'volume': volume}
        strategy.run_update_price(msg)

    # calculate what the earnings would be for buy and hold:
    amount = initial_balance_usd / first_buy_price
    final_balance_usd = amount * last_sell_price
    print("Buy and hold results:")
    print("\tInitial balance USD={}".format(initial_balance_usd))
    print("\tFinal balance USD={}".format(round(final_balance_usd, 2)))
    total = strategy.accnt.market_price * strategy.accnt.balance + strategy.accnt.quote_currency_balance
    print("scotts_smma results:")
    print("\tInitial balance USD={}".format(initial_balance_usd))
    print("\tFinal balance USD={}".format(total))

if __name__ == '__main__':
        ticker_id = 'BTC-USD'
        accnt = AccountSimulate(None, 'BTC', 'USD')
        accnt.set_balance(1000.0)
        #strategy = select_strategy('macd_signal_strategy', None, 'BTC', 'USD', accnt)
        strategy = select_strategy('quadratic_with_fibonacci', None, 'BTC', 'USD', accnt)
        conn = sqlite3.connect('{}_klines.db'.format(ticker_id.replace('-', '_')))

        # start the Web API
        thread = threading.Thread(target=WebThread, args=(strategy,))
        thread.daemon = True
        thread.start()

        simulate(conn, strategy)
        strategy.order_handler.print_run_stats()
        conn.close()
