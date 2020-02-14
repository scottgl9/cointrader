#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.kraken.kraken.krakenex.api import API
from trader.account.kraken.kraken.pykrakenapi import KrakenAPI
from trader.config import *

if __name__ == '__main__':
    api = API(key=KRAKEN_API_KEY, secret=KRAKEN_SECRET_KEY)
    client = KrakenAPI(api=api)
    print(client.get_tradable_asset_pairs())
    print(client.get_trades_history())
    print(api.query_private('OpenPositions')['result'])
    print(client.get_account_balance())
    #print(client.get_account_balance())
    #accnt = AccountCoinbasePro(client=client)
    #balances = accnt.get_account_balances()
    #print(balances)
    #symbols = accnt.get_all_ticker_symbols()
    #print(symbols)
    #accnt.get_info_all_assets()
    #accnt_assets = accnt_info['assets']
    #assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    #for asset in assets:
    #    print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    #print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
    #                                                        accnt_info['total']['btc'],
    #                                                        accnt_info['total']['bnb']))
