#!/usr/bin/env python3
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
from trader.config import *
import trader.account.robin_stocks as r

login = r.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS)
print(login)
