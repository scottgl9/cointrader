#!/usr/bin/env python3
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
from trader.config import *
import pyotp
import trader.account.robin_stocks as r

totp = pyotp.TOTP(ROBINHOOD_2FA_KEY)
mfa_code = totp.now()
print("mfa_code={}".format(mfa_code))
login = r.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS, mfa_code=mfa_code)
print(login)
#print(r.get_currency_pairs())
#print(r.get_markets())
print(r.load_account_profile())
#print(r.load_crypto_profile())
for info in r.get_crypto_positions():
    print(info)