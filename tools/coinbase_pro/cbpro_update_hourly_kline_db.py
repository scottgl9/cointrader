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

def check_duplicates(c):
    for symbol in get_table_list(c):
        cur = c.cursor()
        sql = "SELECT ts, COUNT(*) c FROM {} GROUP BY ts HAVING c > 1;".format(symbol)
        result = cur.execute(sql)
        count=0
        for row in result:
            count += 1
        if count:
            print("{}: {} Duplicate entries found".format(symbol, count))

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
    if len(symbol) <= 5:
        print("{}: \t\t{} \t{}".format(symbol, start_date, end_date))
    else:
        print("{}: \t{} \t{}".format(symbol, start_date, end_date))

def remove_outdated_tables(conn, end_ts):
    table_remove_list = []
    cur = conn.cursor()
    for symbol in get_table_list(conn):
            cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
            result = cur.fetchone()
            end_ts_table = int(result[0])
            if end_ts_table < (end_ts - 1000 * 3600 * 24):
                table_remove_list.append(symbol)
    for symbol in table_remove_list:
        print("Removing table {}".format(symbol))
        cur.execute("DROP TABLE {}".format(symbol))
    conn.commit()

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
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('--update', action='store_true', dest='update',
                        default=False,
                        help='Update tables in hourly kline sqlite db with most recent klines')

    parser.add_argument('--list-dates', action='store_true', dest='list_table_dates',
                        default=False,
                        help='List table names with date ranges in db')

    parser.add_argument('--check-duplicates', action='store_true', dest='check_duplicates',
                        default=False,
                        help='Check for duplicate entries in db')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    parser.add_argument('-r', action='store_true', dest='remove_outdated_tables',
                        default=False,
                        help='Remove outdated tables on update')


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
    accnt.load_exchange_info()

    if results.update:
        end_ts = int(time.mktime(datetime.today().timetuple()) * 1000.0)
        for symbol in get_table_list(conn):
            update_table(conn, client, symbol, end_ts)
        if results.remove_outdated_tables:
            remove_outdated_tables(conn, end_ts)
    elif results.check_duplicates:
        check_duplicates(conn)

    conn.close()
