#!/usr/bin/env python3

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

from trader.account.cbadv.AccountCoinbaseAdvanced import AccountCoinbaseAdvanced
from trader.config import *

if __name__ == '__main__':
    accnt = AccountCoinbaseAdvanced(simulate=False)
    print("getting account balances")
    balances = accnt.get_account_balances()
    print(balances)
    #print(client.get_fees())
    print("USD Total: {} USD".format(accnt.get_account_total_value('USD')))
    accnt.get_exchange_info()
    info = accnt.get_asset_info()
    for i in info:
        print(i)
    for crypto, balance in balances.items():
        print(f"{crypto}: {balance}")