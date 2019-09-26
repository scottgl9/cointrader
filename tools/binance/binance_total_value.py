#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.AccountBinance import AccountBinance
from trader.account.binance import client
from trader.config import *

if __name__ == '__main__':
    client = client.Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client)
    accnt.load_exchange_info()
    accnt_info = accnt.get_account_total_value()
    accnt_assets = accnt_info['assets']
    assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    for asset in assets:
        print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
                                                            accnt_info['total']['btc'],
                                                            accnt_info['total']['bnb']))
