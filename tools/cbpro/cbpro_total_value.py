#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbpro.cbpro import AuthenticatedClient
from trader.account.cbpro.AccountCoinbasePro import AccountCoinbasePro
from trader.config import *

if __name__ == '__main__':
    client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
    accnt = AccountCoinbasePro(client=client, simulate=False)
    #balances = accnt.get_account_balances()
    #print(balances)
    print(client.get_fees())
    print("USD Total: {} USD".format(accnt.get_account_total_value()))
    print("BTC Total: {} BTC".format(accnt.get_account_total_value('BTC')))
    #ts = int(datetime.timestamp(datetime.now()))
    #print(ts)
    #print(accnt.ts_to_iso8601(ts))
    #symbols = accnt.get_all_ticker_symbols()
    #print(symbols)
    #accnt.load_exchange_info()
    #accnt_assets = accnt_info['assets']
    #assets = sorted(accnt_assets, key=lambda x: (accnt_assets[x]['usd']), reverse=True)
    #for asset in assets:
    #    print("{: >5}: {: >15} {: >10} USD\t{: >20} BTC".format(asset, accnt_assets[asset]['amount'], round(accnt_assets[asset]['usd'], 2), accnt_assets[asset]['btc']))

    #print("\nTotal balance USD = {}, BTC={}, BNB={}".format(accnt_info['total']['usd'],
    #                                                        accnt_info['total']['btc'],
    #                                                        accnt_info['total']['bnb']))
