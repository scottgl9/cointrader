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
from trader.account.cbpro import AuthenticatedClient, PublicClient
from trader.account.AccountCoinbasePro import AccountCoinbasePro


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
                        default='cbpro_hourly_klines',
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

    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client, logger=logger, simulation=False)
    accnt.load_exchange_info()

    symbol_table_list = []
    symbols = accnt.get_exchange_pairs()
    for symbol in symbols:
        if symbol.endswith('GBP') or symbol.endswith('EUR'):
            continue
        symbol_table_list.append(symbol)
    print(symbol_table_list)

    db_conn = create_db_connection(db_file)
    columns = "ts integer,low real,high real,open real,close real,volume real"
    cnames = "ts, low, high, open, close, volume"

    start_ts = int(time.mktime(time.strptime(results.start_date, "%m/%d/%Y")))
    end_ts = int(time.mktime(time.strptime(results.end_date, "%m/%d/%Y")))

    print(accnt.ts_to_iso8601(start_ts))
    print(accnt.ts_to_iso8601(end_ts))

    last_ts = 0
    last_kline = None

    for symbol in symbol_table_list:
        print("Processing {} klines...".format(symbol))
        table_symbol = symbol.replace('-', '_')
        # kline format:  [ ts, low, high, open, close, volume ]
        cur = db_conn.cursor()
        cur.execute("""CREATE TABLE {} ({})""".format(table_symbol, columns))
        sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?)""".format(table_symbol, cnames)
        klines = accnt.get_hourly_klines(symbol, start_ts, end_ts)

        last_ts = 0
        last_kline = None

        for k in klines:
            cur_ts = int(k[0])
            # skip if is not an hourly ts
            if not accnt.is_hourly_ts(cur_ts):
                print("{}: skipping {}".format(symbol, cur_ts))
                continue
            cur = db_conn.cursor()
            # check for gaps in hourly klines, for gaps fill with previous kline
            if last_kline and int(cur_ts - last_ts) != 3600:
                print("{}: gap from {} to {}, filling...".format(symbol, last_ts, cur_ts))
                ts = last_ts + 3600
                while ts < cur_ts:
                    last_kline[0] = int(ts)
                    cur.execute(sql, last_kline)
                    ts += 3600
            cur.execute(sql, k)
            last_ts = cur_ts
            last_kline = k
        # ts1 = start_ts
        # count = 0
        # while ts1 <= end_ts:
        #     ts2 = ts1 + 3600 * 250
        #     print(ts1, ts2)
        #     klines = accnt.get_hourly_klines(symbol, ts1, ts2)
        #     ts1 = ts2 + 3600
        #     if not isinstance(klines, list):
        #         if klines['message'] == 'NotFound':
        #             time.sleep(1)
        #             continue
        #         print(klines['message'])
        #         sys.exit(-1)
        #
        #     last_ts = 0
        #     last_kline = None
        #
        #     for kline in klines:
        #         cur_ts = int(kline[0])
        #         if not accnt.is_hourly_ts(cur_ts):
        #             print("{}: skipping {}".format(symbol, cur_ts))
        #             continue
        #         if last_kline and int(cur_ts - last_ts) != 3600:
        #             print("{}: gap from {} to {}, filling...".format(symbol, last_ts, cur_ts))
        #             ts = last_ts + 3600
        #             while ts < cur_ts:
        #                 last_kline[0] = int(ts)
        #                 cur.execute(sql, last_kline)
        #                 ts += 3600
        #         try:
        #             cur.execute(sql, kline)
        #         except sqlite3.ProgrammingError:
        #             print("SQLITE ERROR")
        #             sys.exit(-1)
        #         last_ts = cur_ts
        #         last_kline = kline
        #     time.sleep(1)
        db_conn.commit()
    db_conn.close()
