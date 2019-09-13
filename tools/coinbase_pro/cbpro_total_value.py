#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbpro import AuthenticatedClient, PublicClient
from trader.account.AccountCoinbasePro import AccountCoinbasePro
from trader.account.binance import client
from trader.config import *

if __name__ == '__main__':
    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client)
    balances = accnt.get_account_balances()
    print(balances)
    #accnt_assets = accnt_info['assets']
    #assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    #for asset in assets:
    #    print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    #print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
    #                                                        accnt_info['total']['btc'],
    #                                                        accnt_info['total']['bnb']))
