#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.binance.websockets import BinanceSocketManager
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
import collections
import logging
from trader.config import *


#logger = logging.getLogger(__name__)

# {u'c': u'0.00035038', u'E': 1521434160493, u'h': u'0.00037032', u'l': u'0.00033418', u'o': u'0.00033855', u'q': u'361.61821435', u's': u'BATETH', u'v': u'1044884.00000000', u'e': u'24hrMiniTicker'}

# GDAX kline format: [ timestamp, low, high, open, close, volume ]

class BinanceTrader:
    def __init__(self, client, asset_info=None, volumes=None, logger=None):
        self.client = client
        self.tickers = {}
        self.multitrader = MultiTrader(client,
                                       'momentum_swing_strategy', #'macd_signal_strategy',
                                       assets_info=assets_info,
                                       volumes=volumes,
                                       simulate=False,
                                       logger=logger)

    def get_websocket_kline(self, msg):
        kline = list()
        kline.append(int(msg['E']))
        kline.append(float(msg['l']))
        kline.append(float(msg['h']))
        kline.append(float(msg['o']))
        kline.append(float(msg['c']))
        kline.append(float(msg['v']))
        return kline

    # update tickers dict to contain kline ticker values for all traded symbols
    def process_websocket_message(self, msg):
        for ticker in msg:
            if 's' not in ticker or 'E' not in ticker: continue
            self.tickers[ticker['s']] = self.get_websocket_kline(ticker)
            return self.tickers[ticker['s']]

    def process_message(self, msg):
        self.process_websocket_message(msg)
        self.multitrader.process_message(msg)

    def run(self):
        bm = BinanceSocketManager(self.client)
        bm.start_miniticker_socket(self.process_message)
        #bm.daemon = True
        try:
            bm.start()
            #bm.join()
        except (KeyboardInterrupt, SystemExit):
            sys.exit(0)


def get_prices_from_klines(klines):
    prices = []
    for k in klines:
        prices.append(k[3])
        prices.append(k[4])
    return prices


def get_products_sorted_by_volume(client, currency='BTC'):
    products = client.get_products()
    tickers = client.get_all_tickers()
    pdict = {}
    volumes = {}
    prices = {}

    for product in products.values()[0]:
        if 'quoteAsset' in product and product['quoteAsset'] == currency and product['active']:
            pdict[product['symbol']] = product

    for ticker in tickers:
        if ticker['symbol'].endswith(currency) == False: continue
        if ticker['symbol'] not in pdict.keys(): continue

        # fraction_movement = count_frames_direction_from_klines_name(ticker['symbol'])
        # print(fraction_movement)
        # if fraction_movement < 1.0: continue

        product = pdict[ticker['symbol']]
        #percent = ((float(ticker['price']) - float(product['open'])) / float(product['open'])) * 100.0
        # if percent <= 0.0: continue
        # if float(ticker['price']) < (float(product['high']) + float(product['low'])) / 2.0: continue
        volumes[ticker['symbol']] = float(product['volume'])
        prices[ticker['symbol']] = [product['baseAsset'], float(ticker['price']), float(product['low']), float(product['high'])]
        # ticker['symbol']
    volumes = sorted(volumes.iteritems(), key=lambda (k, v): (v, k), reverse=True)

    buy_list = collections.OrderedDict()
    sell_list = collections.OrderedDict()

    #volumes = volumes[0:len(volumes) / 4]

    # get only the top half of the sorted list by volume
    for symbol, volume in volumes:
        baseAsset = prices[symbol][0]
        price = prices[symbol][1]
        low = prices[symbol][2]
        high = prices[symbol][3]
        mid = (low + high) / 2.0
        if price < (low + mid) / 2.0:
            buy_list[baseAsset] = [price, low, high]
        elif price > (high + mid) / 2.0:
            sell_list[baseAsset] = [price, low, high]

    return buy_list, sell_list, volumes


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
            minQty = ''
            tickSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
            assets[asset['symbol']] = {'minQty': minQty,'tickSize': tickSize}
    return assets


def get_asset_balances(client):
    balances = {}
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) == 0.0 and float(accnt['locked']) == 0.0:
            continue

        balances[accnt['asset']] = float(accnt['free']) + float(accnt['locked'])
    return balances


def filter_assets_by_minqty(assets_info, balances):
    currencies = ['BTC', 'ETH', 'BNB', 'USDT']
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
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "trader"))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    client = Client(MY_API_KEY, MY_API_SECRET)
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    print(balances)
    buy_list = []
    sell_list = []
    currency_list = ['BTC', 'ETH', 'BNB', 'USDT']

    volumes_list = collections.OrderedDict()

    for currency in currency_list:
        if 1: #currency in balances.keys():
            buy, sell, volumes = get_products_sorted_by_volume(client, currency)
            for k,v in volumes:
                volumes_list[k] = v
            for symbol in buy.keys():
                buy_list.append("{}{}".format(symbol, currency))
            for symbol in sell.keys():
                if symbol not in balances.keys():
                    continue
                sell_list.append("{}{}".format(symbol, currency))

    bt = BinanceTrader(client, assets_info, volumes=volumes_list, logger=logger)
    try:
        bt.run()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
