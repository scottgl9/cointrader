#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import time
import logging
import sys
import os
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from trader.config import *
from trader.account.binance.client import Client
from trader.account.AccountBinance import AccountBinance

def get_table_list(c):
    result = []
    res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for name in res:
        result.append(name[0])
    return result

def list_table_dates(c, symbol):
    cur = conn.cursor()
    cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    result = cur.fetchone()
    end_ts = int(result[0] / 1000)
    cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(symbol))
    result = cur.fetchone()
    start_ts = int(result[0] / 1000)

    start_date = time.ctime(start_ts)
    end_date = time.ctime(end_ts)
    print("{}: \t{} \t{}".format(symbol, start_date, end_date))

def update_table(conn, client, symbol, end_ts):
    cur = conn.cursor()
    cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    result = cur.fetchone()
    start_ts = result[0]
    print("Getting {} through {} for {}".format(start_ts, end_ts, symbol))
    cnames = "ts, open, high, low, close, base_volume, quote_volume, trade_count, taker_buy_base_volume, taker_buy_quote_volume"
    klines = client.get_historical_klines_generator(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1HOUR,
        start_str=start_ts,
        end_str=end_ts,
    )

    sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(symbol, cnames)

    for k in klines:
        if k[0] == start_ts:
            continue
        del k[6]
        k = k[:-1]
        cur = conn.cursor()
        cur.execute(sql, k)
    conn.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('--update', action='store_true', dest='update',
                        default=False,
                        help='Update tables in hourly kline sqlite db with most recent klines')

    parser.add_argument('--list-dates', action='store_true', dest='list_table_dates',
                        default=False,
                        help='List table names with date ranges in db')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    if results.list_table_names:
        for symbol in get_table_list(conn):
            print(symbol)
        conn.close()
        sys.exit(0)

    if results.list_table_dates:
        for symbol in get_table_list(conn):
            list_table_dates(conn, symbol)
        conn.close()
        sys.exit(0)

    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, logger=logger)
    accnt.load_info_all_assets()
    accnt.load_detail_all_assets()

    if results.update:
        end_ts = int(time.mktime(datetime.today().timetuple()) * 1000.0)
        for symbol in get_table_list(conn):
            update_table(conn, client, symbol, end_ts)

    conn.close()
