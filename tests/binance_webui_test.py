#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

from trader.account.binance.binance.websockets import BinanceSocketManager
from trader.account.binance.binance.client import Client
from trader.MultiTrader import MultiTrader
import collections
from trader.config import *
import logging
import threading
import sys
from trader.WebHandler import WebThread

logger = logging.getLogger(__name__)

# {u'c': u'0.00035038', u'E': 1521434160493, u'h': u'0.00037032', u'l': u'0.00033418', u'o': u'0.00033855', u'q': u'361.61821435', u's': u'BATETH', u'v': u'1044884.00000000', u'e': u'24hrMiniTicker'}

# GDAX kline format: [ timestamp, low, high, open, close, volume ]

class BinanceTrader:
    def __init__(self, client, asset_info=None, volumes=None):
        self.client = client
        self.tickers = {}
        #self.symbols = symbols #sget_all_tickers(client)
        #print("loading symbols {}".format(self.symbols))
        #accnt = AccountBinance(client, simulation=True)
        self.multitrader = MultiTrader(client, 'null_strategy', assets_info=assets_info, volumes=volumes)
        # start Web API
        thread = threading.Thread(target=WebThread, args=(None, self.multitrader,))
        thread.daemon = True
        thread.start()

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
            if 's' not in ticker or 'E' not in ticker or '': continue
            self.tickers[ticker['s']] = self.get_websocket_kline(ticker)
            return self.tickers[ticker['s']]

    def process_message(self, msg):
        self.process_websocket_message(msg)
        self.multitrader.process_message(msg)

    def run(self):
        bm = BinanceSocketManager(self.client)
        #bm.start_aggtrade_socket(self.accnt.ticker_id, self.process_message)
        bm.start_miniticker_socket(self.process_message)
        bm.start()


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

    #volumes = volumes[0:len(volumes) / 5]

    return volumes

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
    #print(get_products_by_volume(client))
    client = Client(MY_API_KEY, MY_API_SECRET)
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    currency_list = ['BTC', 'ETH', 'BNB', 'USDT']
    #print(assets_info)
    volumes_list = collections.OrderedDict()

    for currency in currency_list:
        volumes = get_products_sorted_by_volume(client, currency)
        for k,v in volumes:
            volumes_list[k] = v

    bt = BinanceTrader(client, assets_info, volumes=volumes_list)
    try:
        bt.run()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

