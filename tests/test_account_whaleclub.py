#!/usr/bin/python

from trader.account.whaleclub import Client
from trader.config import *

if __name__ == '__main__':
    client = Client(api_token=WC_BTC_DEMO_API_KEY)
    print(client.get_active_contracts())
    print(client.get_balance())
    crypto_ticker_ids = []
    for name, info in client.get_all_markets().items():
        if info['category'] == 'crypto':
            crypto_ticker_ids.append(name)
    print(crypto_ticker_ids)
    symbol_list2 = None
    if len(crypto_ticker_ids) > 5:
        symbol_list = ','.join(crypto_ticker_ids[0:4])
        symbol_list2 = ','.join(crypto_ticker_ids[4:])
        print(symbol_list)
        print(symbol_list2)
    else:
        symbol_list = ','.join(crypto_ticker_ids)

    prices = {}
        #print(client.get_markets(symbol_list=symbol_list))
    for name, info in client.get_price(symbol_list=symbol_list).items():
        prices[name] = [info['bid'], info['ask']]

    if symbol_list2:
        for name, info in client.get_price(symbol_list=symbol_list2).items():
            prices[name] = [info['bid'], info['ask']]

    print(prices)
    print(client.get_active_contracts())
