#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.bittrex.bittrex import Bittrex
from trader.account.bittrex.AccountBittrex import AccountBittrex, API_V2_0
from trader.config import *

if __name__ == '__main__':
    client = Bittrex(api_key=BITTREX_API_KEY, api_secret=BITTREX_API_SECRET, api_version=API_V2_0)
    accnt = AccountBittrex(client=client)
    balances = accnt.get_account_balances()
    print(balances)
    tickers = accnt.get_all_tickers()
    print(tickers)
    #accnt_assets = accnt_info['assets']
    #assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    #for asset in assets:
    #    print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    #print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
    #                                                        accnt_info['total']['btc'],
    #                                                        accnt_info['total']['bnb']))
