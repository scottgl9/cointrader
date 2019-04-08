#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.binance.websockets import BinanceSocketManager
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.lib.Kline import Kline
import argparse
import collections
import logging
import threading
import signal
import time
from trader.WebHandler import WebThread
from trader.config import *


#logger = logging.getLogger(__name__)

# {u'c': u'0.00035038', u'E': 1521434160493, u'h': u'0.00037032', u'l': u'0.00033418', u'o': u'0.00033855', u'q': u'361.61821435', u's': u'BATETH', u'v': u'1044884.00000000', u'e': u'24hrMiniTicker'}

# GDAX kline format: [ timestamp, low, high, open, close, volume ]

class BinanceTrader:
    def __init__(self, client, strategy, signal_name, logger=None):
        self.client = client
        self.found = False
        self.logger = logger
        self.kline = None
        self.tickers = {}
        self.multitrader = MultiTrader(client,
                                       strategy,
                                       signal_names=[signal_name],
                                       simulate=False,
                                       logger=logger)

        logger.info("Started live trading strategy: {} signal: {}".format(strategy, signal_name))

        # start the Web API
        self.thread = threading.Thread(target=WebThread, args=(self.multitrader,))
        self.thread.daemon = True
        self.thread.start()

    def set_sell_only(self):
        if self.multitrader and self.multitrader.accnt:
            self.multitrader.accnt.set_sell_only(True)

    def set_btc_only(self):
        if self.multitrader and self.multitrader.accnt:
            self.multitrader.accnt.set_btc_only(True)

    def set_trades_disabled(self):
        if self.multitrader and self.multitrader.accnt:
            self.multitrader.accnt.set_trades_disabled(True)

    def set_test_stop_loss(self):
        if self.multitrader and self.multitrader.accnt:
            self.multitrader.accnt.set_test_stop_loss(True)

    def set_max_market_buy(self, max_market_buy):
        if self.multitrader and self.multitrader.accnt:
            self.multitrader.accnt.set_max_market_buy(max_market_buy)

    # process message about user account update
    def process_user_message(self, msg):
        try:
            symbol = msg['s']
            cmd = msg['X']
            type = msg['o']
            side = msg['S']
            price = msg['p']
            size = msg['q']
        except KeyError:
            return

        # log json response
        self.logger.info(msg)

        self.multitrader.process_user_message(msg)

        self.logger.info("{}: cmd={} type={} side={} price={} size={}".format(
            symbol,
            cmd,
            type,
            side,
            price,
            size
        ))

    def process_message(self, msg):
        #self.process_websocket_message(msg)

        if not self.found and 'BTCUSDT' in self.tickers.keys():
            if self.multitrader.accnt.total_btc_available():
                self.found = True
                #total_btc = multitrader.accnt.balances['BTC']['balance']
                total_btc = self.multitrader.accnt.get_total_btc_value()
                self.multitrader.initial_btc_total = total_btc
                print("Initial BTC={}".format(total_btc))

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return

            if not self.kline:
                self.kline = Kline(symbol=msg['s'],
                                   open=float(msg['o']),
                                   close=float(msg['c']),
                                   low=float(msg['l']),
                                   high=float(msg['h']),
                                   volume_base=float(msg['v']),
                                   volume_quote=float(msg['q']),
                                   ts=int(msg['E']))
            else:
                self.kline.symbol = msg['s']
                self.kline.open = float(msg['o'])
                self.kline.close = float(msg['c'])
                self.kline.low = float(msg['l'])
                self.kline.high = float(msg['h'])
                self.kline.volume_base = float(msg['v'])
                self.kline.volume_quote = float(msg['q'])
                self.kline.volume = self.kline.volume_quote
                self.kline.ts = int(msg['E'])

            self.multitrader.process_message(self.kline)
        else:
            for part in msg:
                if 's' not in part.keys(): continue

                if not self.kline:
                    self.kline = Kline(symbol=part['s'],
                                       open=float(part['o']),
                                       close=float(part['c']),
                                       low=float(part['l']),
                                       high=float(part['h']),
                                       volume_base=float(part['v']),
                                       volume_quote=float(part['q']),
                                       ts=int(part['E']))
                else:
                    self.kline.symbol = part['s']
                    self.kline.open = float(part['o'])
                    self.kline.close = float(part['c'])
                    self.kline.low = float(part['l'])
                    self.kline.high = float(part['h'])
                    self.kline.volume_base = float(part['v'])
                    self.kline.volume_quote = float(part['q'])
                    self.kline.volume = self.kline.volume_quote
                    self.kline.ts = int(part['E'])

                self.multitrader.process_message(self.kline)

    def run(self):
        self.bm = BinanceSocketManager(self.client)
        self.bm.daemon = True
        self.bm.start_miniticker_socket(self.process_message)
        self.bm.start_user_socket(self.process_user_message)
        self.bm.start()
        while True:
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                self.bm.close()
                #self.bm.join()
                break


#def get_prices_from_klines(klines):
#    prices = []
#    for k in klines:
#        prices.append(k[3])
#        prices.append(k[4])
#    return prices

def get_all_tickers(client):
    result = []
    for key, value in client.get_exchange_info().items():
        if key != 'symbols': continue
        for asset in value:
            #if asset['symbol'].endswith('USDT'): continue
            result.append(asset['symbol'])
    return result


def get_info_all_assets(client):
    assets = {}
    for key, value in client.get_exchange_info().items():
        if key != 'symbols':
            continue
        for asset in value:
            minNotional = ''
            minQty = ''
            tickSize = ''
            stepSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
                if 'stepSize' in filter:
                    stepSize = filter['stepSize']
                if 'minNotional' in filter:
                    minNotional = filter['minNotional']

            assets[asset['symbol']] = {'minQty': minQty,
                                       'tickSize': tickSize,
                                       'stepSize': stepSize,
                                       'minNotional': minNotional
                                       }

    return assets


def get_asset_balances(client):
    balances = {}
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) == 0.0 and float(accnt['locked']) == 0.0:
            continue

        balances[accnt['asset']] = float(accnt['free']) + float(accnt['locked'])
    return balances


def filter_assets_by_minqty(assets_info, balances):
    currencies = ['BTC', 'ETH', 'BNB', 'PAX', 'USDT']
    result = {}
    for name, balance in balances.items():
        for currency in currencies:
            symbol = "{}{}".format(name, currency)
            if symbol not in assets_info.keys(): continue

            minQty = float(assets_info[symbol]['minQty'])
            if float(balance) >= minQty:
                result[name] = balance
    return result


def filter_by_balances(assets, balances):
    if len(assets) == 0: return assets
    result = []
    for name, info in assets.items():
        print(name, info)
        if name in balances.keys():
          result.append(name)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', action='store', dest='strategy',
                        default='basic_signal_market_strategy',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_name',
                        default='Hybrid_Crossover_Test',
                        help='name of signal to use')

    parser.add_argument('--sell-only', action='store_true', dest='sell_only',
                        default=False,
                        help='Set to sell only mode')

    parser.add_argument('--btc-only', action='store_true', dest='btc_only',
                        default=False,
                        help='Only buy/sell BTC currency trade pairs')

    parser.add_argument('--trades-disabled', action='store_true', dest='trades_disabled',
                        default=False,
                        help='Disable buy/sell trading')

    parser.add_argument('--max-market-buy', action='store', dest='max_market_buy',
                        default=0,
                        help='Maxmimum number of open market buys without matching sells')

    parser.add_argument('--test-stop-loss', action='store_true', dest='test_stop_loss',
                        default=False,
                        help='Test stop loss orders')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "trader"))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

    client = Client(MY_API_KEY, MY_API_SECRET)
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    logger.info(balances)
    buy_list = []
    sell_list = []
    currency_list = ['BTC', 'ETH', 'BNB', 'PAX', 'USDT']

    bt = BinanceTrader(client, strategy=results.strategy, signal_name=results.signal_name, logger=logger)
    if results.sell_only:
        logger.info("Setting SELL ONLY mode")
        bt.set_sell_only()
    if results.trades_disabled:
        logger.info("Setting TRADES DISABLED mode")
        bt.set_trades_disabled()
    if results.test_stop_loss:
        logger.info("Setting TEST_STOP_LOSS mode")
        bt.set_test_stop_loss()
    bt.set_max_market_buy(int(results.max_market_buy))
    bt.run()
