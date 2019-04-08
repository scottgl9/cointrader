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

    start_ts = int(time.mktime(time.strptime(results.start_date, "%d/%m/%Y"))) * 1000
    end_ts = int(time.mktime(time.strptime(results.end_date, "%d/%m/%Y"))) * 1000
    print(start_ts, end_ts)
    client = Client(MY_API_KEY, MY_API_SECRET)
    print("Getting klines from {} to {} for {}".format(results.start_date, results.end_date, results.symbol))
    klines = client.get_historical_klines_generator(
        symbol=results.symbol,
        interval=Client.KLINE_INTERVAL_1HOUR,
        start_str=start_ts,
        end_str=end_ts,
    )
