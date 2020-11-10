#!/usr/bin/env python3

import sys
import pyotp
try:
    import trader
except ImportError:
    sys.path.append('.')

try:
    import trader.account.robinhood.robin_stocks as client
except ImportError:
    import robin_stocks as client
from trader.account.robinhood.AccountRobinhood import AccountRobinhood
from trader.lib.struct.Exchange import Exchange
from trader.config import *

def get_watched_symbols(client):
    watchlists = []
    symbols = []
    for result in client.get_all_watchlists():
        watchlists.append(result['name'])
    for wl in watchlists:
        result = client.get_watchlist_by_name(name=wl)
        for e in result:
            symbols.append(client.get_symbol_by_url(e['instrument']))
    return symbols

if __name__ == '__main__':
    totp = pyotp.TOTP(ROBINHOOD_2FA_KEY)
    mfa_code = totp.now()
    print("MFA: {}".format(mfa_code))
    login = client.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS, mfa_code=mfa_code)
    print(login)
    accnt = AccountRobinhood(client=client, simulate=False)
    accnt.set_account_mode(Exchange.ACCOUNT_MODE_STOCKS)
    accnt.load_exchange_info()
    print(accnt.get_ticker_symbols())
    #print(accnt.get_tickers())
    #accnt.get_ticker('BTC-USD')
    print(accnt.get_account_balances())
