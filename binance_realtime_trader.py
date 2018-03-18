#!/usr/bin/python

from trader.account.binance.websockets import BinanceSocketManager
from trader.account.binance.client import Client
from trader.AccountBinance import AccountBinance
from trader.strategy import select_strategy

from config import *

class BinanceTrader:
    def __init__(self, client):
        self.client = client
        self.accnt = AccountBinance(self.client, 'BNB', 'BTC')
        self.trader = select_strategy('trailing_prices_strategy', self.client, 'BTC', 'USD',
                                      account_handler=self.accnt, order_handler=None) #self.order_handler)

        self.order_handler = self.trader.order_handler
        print(self.accnt)
        self.accnt.get_account_balance()

    def process_message(self, msg):
        if 'p' in msg:
            print(msg)
            price = float(msg["p"])
            self.trader.run_update_price(price)

    def run(self):
        bm = BinanceSocketManager(self.client)
        bm.start_aggtrade_socket(self.accnt.ticker_id, self.process_message)
        bm.start()


def get_products_volumes(client, currency='BTC'):
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

    buy_list = []
    sell_list = []

    for symbol, volume in volumes[0:len(volumes)/2]:
        baseAsset = prices[symbol][0]
        price = prices[symbol][1]
        low = prices[symbol][2]
        high = prices[symbol][3]
        mid = (low + high) / 2.0
        if price < (low + low + mid) / 3.0:
            buy_list.append([baseAsset, price, low, high])
        elif price > (high + high + mid) / 3.0:
            buy_list.append([baseAsset, price, low, high])

    return buy_list, sell_list

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
    currencies = ['BTC', 'ETH']
    result = {}
    for name, balance in balances.items():
        for currency in currencies:
            if name == 'BTC': continue
            if name == currency: continue
            symbol = "{}{}".format(name, currency)
            minQty = float(assets_info[symbol]['minQty'])
            if float(balance) >= minQty:
                result[name] = balance
    return result

def filter_by_balances(assets, balances):
    if len(assets) == 0: return assets
    result = []
    for asset in assets:
        if asset[0] in balances.keys():
          result.append(asset)
    return result

if __name__ == '__main__':
    #print(get_products_by_volume(client))
    client = Client(MY_API_KEY, MY_API_SECRET)
    #bt = BinanceTrader(client)
    #bt.run()
    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    print(balances)
    buy_list, sell_list = get_products_volumes(client, 'ETH')
    print("buy list:")
    print(filter_by_balances(buy_list, balances))
    print("sell list:")
    print(filter_by_balances(sell_list, balances))