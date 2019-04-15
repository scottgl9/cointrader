#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
import argparse

def get_table_list(c):
    result = []
    res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for name in res:
        result.append(name[0])
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('--update', action='store_true', dest='update',
                        default=False,
                        help='Update tables in hourly kline sqlite db with most recent klines')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename

    print("Loading {}".format(filename))
    conn = sqlite3.connect(filename)

    if results.list_table_names:
        for symbol in get_table_list(conn):
            print(symbol)

    conn.close()
