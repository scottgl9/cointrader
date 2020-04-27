#!/usr/bin/env python3
from trader.AccountGDAX import AccountGDAX
from trader.account.gdax.authenticated_client import AuthenticatedClient
from trader.config import *

if __name__ == '__main__':
    auth_client = AuthenticatedClient(GDAX_KEY, GDAX_SECRET, GDAX_PASS)
    accnt = AccountGDAX(auth_client, 'BTC', 'USD', simulate=False)
    print(accnt.get_account_balance())
    print(accnt.get_fills())
    print(accnt.get_orders())
    print(accnt.get_account_history())
    print(accnt.get_deposit_address())
    print(accnt.get_klines())
