#!/usr/bin/python

from trader.account.binance.client import Client
from trader.AccountBinance import AccountBinance
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

    for name, value in balances.items():
        if name == 'BTC' or name == 'ETH' or name == 'BNB' or name == 'USDT':
            continue

        ticker_id = "{}BNB".format(name)
        if ticker_id not in assets_info.keys(): continue
        size = round_base(value, float(assets_info[ticker_id]['minQty']))
        print(ticker_id, size)
        print(client.order_market_sell(symbol=ticker_id, quantity=size))
