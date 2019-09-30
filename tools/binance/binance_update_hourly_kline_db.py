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
from trader.config import *
from trader.account.binance.client import Client
from trader.account.AccountBinance import AccountBinance
from trader.HourlyKlinesDB import HourlyKlinesDB


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

    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, logger=logger)
    accnt.load_exchange_info()
    hkdb = HourlyKlinesDB(accnt=accnt, filename=filename, logger=logger)

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)
        hkdb.close()
        sys.exit(0)

    if results.list_table_dates:
        for symbol in hkdb.get_table_list():
            hkdb.list_table_dates(symbol)
        hkdb.close()
        sys.exit(0)

    if results.check_duplicates:
        hkdb.check_duplicates()
        hkdb.close()
        sys.exit(0)

    if results.update:
        end_ts = int(accnt.seconds_to_ts(time.mktime(datetime.today().timetuple())))
        for table_name in hkdb.get_table_list():
            print("Updating {}".format(table_name))
            hkdb.update_table(table_name=table_name, end_ts=end_ts)
