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
from trader.config import *

if __name__ == '__main__':
    totp = pyotp.TOTP(ROBINHOOD_2FA_KEY)
    mfa_code = totp.now()
    print("MFA: {}".format(mfa_code))
    login = client.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS, mfa_code=mfa_code)
    print(login)
    accnt = AccountRobinhood(client=client, simulate=False)
    accnt.load_exchange_info()
    print(accnt.get_tickers())
    #accnt.get_ticker('BTC-USD')
    print(accnt.get_account_balances())
    #balances = accnt.get_account_balances()
    #print(balances)
    print("USD Total: {} USD".format(accnt.get_account_total_value('USD')))
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
