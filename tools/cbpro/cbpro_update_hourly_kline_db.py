#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import time
import logging
import sys
import os
import argparse
from datetime import datetime
from trader.config import *
from trader.account.cbpro import AuthenticatedClient
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.KlinesDB import KlinesDB


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='db/cbpro_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('--update', action='store_true', dest='update',
                        default=False,
                        help='Update tables in hourly kline sqlite db with most recent klines')

    parser.add_argument('--list-dates', action='store_true', dest='list_table_dates',
                        default=False,
                        help='List table names with date ranges in db')

    parser.add_argument('--check', action='store_true', dest='check_errors',
                        default=False,
                        help='Check hourly kline db tables for errors')

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

    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client, logger=logger, simulation=False)
    accnt.load_exchange_info()
    kdb = KlinesDB(accnt=accnt, filename=filename, logger=logger)

    if results.list_table_names:
        for table_name in kdb.get_table_list():
            print(table_name)
        kdb.close()
        sys.exit(0)

    if results.list_table_dates:
        for table_name in kdb.get_table_list():
            kdb.list_table_dates(table_name)
        kdb.close()
        sys.exit(0)

    if results.check_duplicates:
        kdb.check_tables_duplicates()
        kdb.close()
        sys.exit(0)

    if results.check_errors:
        for table_name in kdb.get_table_list():
            kdb.check_table(table_name)
        kdb.close()
        sys.exit(0)

    if results.update:
        end_ts = int(accnt.seconds_to_ts(time.mktime(datetime.today().timetuple())))
        for table_name in kdb.get_table_list():
            print("Updating {}".format(table_name))
            kdb.update_table(table_name=table_name, end_ts=end_ts, fix_gaps=True)
