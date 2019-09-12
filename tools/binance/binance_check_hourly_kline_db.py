#!/usr/bin/python
# check for errors in hourly kline db

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


def get_table_list(c):
    result = []
    res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for name in res:
        result.append(name[0])
    return result


def check_duplicates(c):
    duplicates_found = False
    for symbol in get_table_list(c):
        cur = c.cursor()
        sql = "SELECT ts, COUNT(*) c FROM {} GROUP BY ts HAVING c > 1;".format(symbol)
        result = cur.execute(sql)
        count=0
        for row in result:
            count += 1
        if count:
            print("{}: {} Duplicate entries found".format(symbol, count))
            duplicates_found = True
    return duplicates_found


def get_timestamps(c, symbol):
    timestamps = []
    cur = c.cursor()
    sql = "SELECT ts FROM {} ORDER BY ts ASC".format(symbol)
    rows = cur.execute(sql)
    for row in rows:
        timestamps.append(row[0])
    return timestamps


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

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

    # check for duplicate entries
    if check_duplicates(conn):
        sys.exit(-1)
    for symbol in get_table_list(conn):
        print("\nChecking table {}".format(symbol))
        timestamps = get_timestamps(conn, symbol)
        for i in range(1, len(timestamps)):
            ts1 = int(timestamps[i - 1])
            ts2 = int(timestamps[i])
            ts_delta = ts2 - ts1
            if ts_delta != 3600000:
                dt_ts1 = datetime.fromtimestamp(int(ts1 / 1000))
                dt_ts2 = datetime.fromtimestamp(int(ts2 / 1000))
                print("Error in table {}:\t{}\t{}\t({})".format(symbol, dt_ts1, dt_ts2, ts_delta / 1000))
    conn.close()
