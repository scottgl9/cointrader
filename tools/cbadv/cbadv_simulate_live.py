#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
from coinbase.rest import RESTClient

import json
import sys
import time
import datetime
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *


if __name__ == '__main__':
    logging.getLogger("coinbase").setLevel(logging.WARNING)
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.WARNING)
    client = RESTClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET)
    accnt = AccountCoinbaseAdvanced(client=client, simulate=False, live=False, logger=logger)
    accnt.get_exchange_info()

    running = True

    product_ids = ['ETH-USD'] #["SOL-ETH", "ADA-ETH", "LINK-ETH"]

    while running:
        try:
            time.sleep(1)
            # check if the current time is a new minute
            if int(time.time()) % 60 == 0:
                print("Getting klines...")
                for id in product_ids:
                    klines = accnt.market.get_klines(days=0, hours=1, minutes=0, ticker_id=id, granularity=60)
                    for kline in klines:
                        # convert start time from unix timestamp to time string
                        dt_object = datetime.datetime.fromtimestamp(float(kline['start']))

                        # Format datetime object to string
                        print(dt_object.strftime("%Y-%m-%d %H:%M:%S"))

                        #print(accnt.ts_to_iso8601(kline['time']))
        except (KeyboardInterrupt, SystemExit):
            running = False
            print("Exiting...")