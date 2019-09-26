#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.poloniex import Poloniex
from trader.account.AccountPoloniex import AccountPoloniex
from trader.config import *

if __name__ == '__main__':
    client = Poloniex(key=POLONIEX_API_KEY, secret=POLONIEX_SECRET_KEY, coach=False)
    accnt = AccountPoloniex(client=client, simulation=False)
    accnt.load_exchange_info()
    #print(client.returnBalances())
    #print(client.returnCompleteBalances())
    #print(client.returnCurrencies())
    #print(client.returnTicker())
    #print(accnt.get_exchange_info())
    #print(accnt.get_all_tickers())
    #print(accnt.get_all_ticker_symbols())
    #accnt = AccountPoloniex(client=client)
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
