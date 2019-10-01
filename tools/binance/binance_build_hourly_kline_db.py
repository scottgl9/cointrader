#!/usr/bin/python

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
import threading
import argparse
from trader.config import *
from trader.account.binance.client import Client
from trader.account.AccountBinance import AccountBinance


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
                        default='binance_hourly_klines',
                        help='base filename of hourly kline sqlite db')

    parser.add_argument('--currency', action='store', dest='currency',
                        default='BTC',
                        help='currency of trade symbols')

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

    currency = results.currency

    if not currency:
        currency = 'BTC'
        db_file = "{}.db".format(results.base_filename)
    else:
        db_file = "{}_{}.db".format(results.base_filename, currency)
    if os.path.exists(db_file):
        logger.info("{} already exists, exiting....".format(db_file))
        sys.exit(0)

    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, logger=logger, simulation=False)
    accnt.load_exchange_info()

    symbol_table_list = []
    for symbol in sorted(accnt.get_all_ticker_symbols(currency)):
        if accnt.get_usdt_value_symbol(symbol) <= 0.02:
            continue
        base_name, currency_name = accnt.split_symbol(symbol)
        if not base_name or not currency_name: continue
        if not accnt.is_asset_available(base_name):
            continue

        symbol_table_list.append(symbol)

    if currency != 'USDT':
        symbol_table_list.append("{}USDT".format(currency))

    db_conn = create_db_connection(db_file)

    start_ts = int(time.mktime(time.strptime(results.start_date, "%m/%d/%Y")))
    end_ts = int(time.mktime(time.strptime(results.end_date, "%m/%d/%Y")))

    columns = "ts integer,open real,high real,low real,close real,volume real"
    cnames = "ts, open, high, low, close, volume"

    current_ts = int(time.time()) * 1000

    for symbol in sorted(symbol_table_list):
        cur = db_conn.cursor()

        print("Getting klines from {} to {} for {}".format(results.start_date, results.end_date, symbol))

        klines = client.get_historical_klines_generator(
                 symbol=symbol,
                 interval=Client.KLINE_INTERVAL_1HOUR,
                 start_str=start_ts * 1000,
                 end_str=end_ts * 1000,
        )

        kline_list = []
        for k in klines:
            k = k[:6]
            #del k[6]
            #k = k[:-1]
            kline_list.append(k)

        if (current_ts - kline_list[-1][0]) > 3600*24*1000:
            print("Skipping {}".format(symbol))
            continue

        cur.execute("""CREATE TABLE {} ({})""".format(symbol, columns))

        sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?)""".format(symbol, cnames)

        last_ts = 0
        last_kline = None

        for k in kline_list:
            cur_ts = int(k[0])
            # skip if is not an hourly ts
            if not accnt.is_hourly_ts(cur_ts):
                # check if the timestamp is less than 1 hr from last_ts or from cur_ts
                #hourly_ts = accnt.get_hourly_ts(cur_ts)
                #if int(hourly_ts - last_ts) < 3600000 or int(cur_ts - hourly_ts) < 3600000:
                print("{}: skipping {}".format(symbol, cur_ts))
                continue
                # correct ts
                #k[0] = int(hourly_ts)
                #cur_ts = int(k[0])
            cur = db_conn.cursor()
            # check for gaps in hourly klines, for gaps fill with previous kline
            if last_kline and int(cur_ts - last_ts) != 3600000:
                print("{}: gap from {} to {}, filling...".format(symbol, last_ts, cur_ts))
                ts = last_ts + 3600000
                while ts < cur_ts:
                    last_kline[0] = int(ts)
                    cur.execute(sql, last_kline)
                    ts += 3600000
            cur.execute(sql, k)
            last_ts = cur_ts
            last_kline = k
        db_conn.commit()
        db_conn.close()
