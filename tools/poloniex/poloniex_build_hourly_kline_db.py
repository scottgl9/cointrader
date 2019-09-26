#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sqlite3
import time
import logging
import os
import sys
import threading
import argparse
from trader.config import *
from trader.account.poloniex import Poloniex
from trader.account.AccountPoloniex import AccountPoloniex


def create_db_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None

if __name__ == '__main__':
    date_today = datetime.today().strftime('%m/%d/%Y')
    date_two_years_ago = "01/01/2017" #(datetime.now() - relativedelta(years=2)).strftime('%m/%d/%Y')

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', dest='base_filename',
                        default='poloniex_hourly_klines',
                        help='base filename of hourly kline sqlite db')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default=date_two_years_ago,
                        help='Start date from which to capture hourly klines (month/day/year)')

    parser.add_argument('--end-date', action='store', dest='end_date',
                        default=date_today,
                        help='End date from which to capture hourly klines (month/day/year)')

    results = parser.parse_args()
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    db_file = "{}.db".format(results.base_filename)
    if os.path.exists(db_file):
        logger.info("{} already exists, exiting....".format(db_file))
        sys.exit(0)

    client = Poloniex(key=POLONIEX_API_KEY, secret=POLONIEX_SECRET_KEY, coach=False)
    accnt = AccountPoloniex(client=client, logger=logger, simulation=False)
    accnt.load_exchange_info()

    symbol_table_list = []
    symbols = accnt.get_exchange_pairs()
    for symbol in symbols:
        base, currency = accnt.split_ticker_id(symbol)
        if not accnt.is_asset_available(base):
            print("Skipping {}".format(symbol))
            continue
        symbol_table_list.append(symbol)
    print(symbol_table_list)

    db_conn = create_db_connection(db_file)
    columns = "date integer,high real,low real,open real,close real,volume real, quoteVolume real, weightedAverage real"
    cnames = "date, high, low, open, close, volume, quoteVolume, weightedAverage"

    start_ts = int(time.mktime(time.strptime(results.start_date, "%m/%d/%Y")))
    end_ts = int(time.mktime(time.strptime(results.end_date, "%m/%d/%Y")))

    for symbol in symbol_table_list:
        print("Processing {} klines...".format(symbol))
        table_symbol = symbol.replace('-', '_')
        # kline format:  [ ts, low, high, open, close, volume ]
        cur = db_conn.cursor()
        cur.execute("""CREATE TABLE {} ({})""".format(table_symbol, columns))
        sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?, ?, ?)""".format(table_symbol, cnames)
        ts = start_ts
        count = 0
        while ts <= end_ts:
            ts2 = ts + 3600 * 250
            klines = accnt.get_hourly_klines(symbol, ts, ts2)
            ts = ts2 + 3600
            for kline in klines:
                # since we are grabbing klines at 30 minute intervals, only add hourly klines
                if not accnt.is_hourly_ts(int(kline['date'])):
                    continue
                data = []
                for name in accnt.hourly_cnames:
                    data.append(kline[name])
                try:
                    cur.execute(sql, data)
                except sqlite3.ProgrammingError:
                    print("SQLITE ERROR")
                    sys.exit(-1)
            time.sleep(1)
        db_conn.commit()
    db_conn.close()
