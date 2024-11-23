#!/usr/bin/env python3
import logging
from coinbase.websocket import WSClient, WebsocketResponse
from coinbase.rest import RESTClient

import json
import sys
import time
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *

class CBADVRealTime:
    low = 0.0
    high = 0.0
    open = 0.0
    close = 0.0
    def on_message(self, msg):
        ws_object = WebsocketResponse(json.loads(msg))
        #print(ws_object.channel)
        if ws_object.channel == "ticker" :
            for event in ws_object.events:
                print(event)
                #for ticker in event.tickers:
                #    print(ticker)
                #    print(ticker.product_id + ": " + ticker.price)
        elif ws_object.channel == "matches":
            for event in ws_object.events:
                print(event)
                #for match in event.matches:
                #    print(match)

if __name__ == '__main__':
    logging.getLogger("coinbase").setLevel(logging.WARNING)
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.WARNING)
    client = RESTClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET)
    rt = CBADVRealTime()
    ws_client = WSClient(api_key=CBADV_KEY, api_secret=CBADV_SECRET, on_message=rt.on_message)
    accnt = AccountCoinbaseAdvanced(client=client, simulate=False, live=False, logger=logger)

    running = True

    product_ids = ["SOL-ETH", "ADA-ETH", "LINK-ETH"]
    ws_client.open()
    ws_client.subscribe(product_ids=product_ids, channels=['ticker']) #, 'matches'])

    while running:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            ws_client.unsubscribe(product_ids=product_ids, channels=['ticker'])#, 'matches'])
            ws_client.close()
            running = False
            print("Exiting...")