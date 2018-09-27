#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

from trader.account.binance.client import Client
from trader.account.AccountBinance import AccountBinance
from trader.strategy import select_strategy
import collections
import matplotlib.pyplot as plt
import sys
from trader.config import *

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

def round_base(price, base_min_size):
    if base_min_size != 0.0:
        return round(price, '{:f}'.format(base_min_size).index('1') - 1)
    return price

def round_quote(price, quote_increment):
    if quote_increment != 0.0:
        return round(price, '{:f}'.format(quote_increment).index('1') - 1)
    return price

def my_float(value):
    return str("{:.8f}".format(float(value)))

if __name__ == '__main__':
    #print(get_products_by_volume(client))
    client = Client(MY_API_KEY, MY_API_SECRET)
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))

    usdt_sell_queue = {}
    btc_sell_queue = {}

    for name, value in balances.items():
        if name == 'USDT':
            continue

        ticker_id = "{}USDT".format(name)
        if ticker_id not in assets_info.keys():
            print("{} doesn't exist, so selling as {}BTC first".format(ticker_id, name))
            ticker_id = "{}BTC".format(name)
            size = round_base(value, float(assets_info[ticker_id]['minQty']))
            if size == 0.0:
                continue
            btc_sell_queue[ticker_id] = size
            continue
        size = round_base(value, float(assets_info[ticker_id]['minQty']))
        if size == 0.0:
            continue
        usdt_sell_queue[ticker_id] = size

    print("BTC sell queue:")
    if len(btc_sell_queue) != 0:
        for ticker_id, size in btc_sell_queue.items():
            print(ticker_id, size)
            print(client.order_market_sell(symbol=ticker_id, quantity=size))

        assets_info = get_info_all_assets(client)
        balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
        usdt_sell_queue['BTCUSDT'] = balances['BTC']

    print("USDT sell queue:")
    if len(usdt_sell_queue) != 0:
        for ticker_id, size in usdt_sell_queue.items():
            print(ticker_id, size)
            print(client.order_market_sell(symbol=ticker_id, quantity=size))
