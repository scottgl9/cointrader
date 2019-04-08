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

if __name__ == '__main__':
    date_today = datetime.today().strftime('%m/%d/%Y')
    date_one_year_ago = (datetime.now() - relativedelta(years=1)).strftime('%m/%d/%Y')

    parser = argparse.ArgumentParser()

    parser.add_argument('--symbol', action='store', dest='symbol',
                        default='',
                        help='Symbol for which to capture hourly klines')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default=date_one_year_ago,
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

    start_ts = int(time.mktime(time.strptime(results.start_date, "%d/%m/%Y")))
    end_ts = int(time.mktime(time.strptime(results.end_date, "%d/%m/%Y")))
    client = Client(MY_API_KEY, MY_API_SECRET)
    print("Getting klines from {} to {} for {}".format(results.start_date, results.end_date, results.symbol))

    filename = "{}_klines.csv".format(results.symbol)
    f = open(filename, "wt")
    f.write("timestamp,open,high,low,close,base_volume,quote_volume,trade_count,taker_buy_base_volume,taker_buy_quote_volume,\n")

    cur_start_ts = start_ts
    cur_end_ts = cur_start_ts + 3600 * 500

    # while cur_end_ts <= end_ts:
    #     klines = client.get_historical_klines(
    #         symbol=results.symbol,
    #         interval=Client.KLINE_INTERVAL_1HOUR,
    #         start_str=cur_start_ts * 1000,
    #         end_str=cur_end_ts * 1000,
    #     )
    #
    #     for kline in klines:
    #         f.write(",".join(map(str, kline)))
    #         f.write(",\n")
    #
    #     cur_start_ts = cur_end_ts
    #     cur_end_ts = cur_start_ts + 3600 * 500
    #     time.sleep(1)

    klines = client.get_historical_klines_generator(
             symbol=results.symbol,
             interval=Client.KLINE_INTERVAL_1HOUR,
             start_str=start_ts * 1000,
             end_str=end_ts * 1000,
    )

    for kline in klines:
        #kline[0] /= 1000
        del kline[6]
        kline = kline[:-1]
        f.write(",".join(map(str, kline)))
        f.write(",\n")

    f.close()
