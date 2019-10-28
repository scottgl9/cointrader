#!/usr/bin/env python3
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
from trader.config import *
from trader.account.Robinhood import Robinhood

rh = Robinhood()
rh.login(username=ROBINHOOD_USER, password=ROBINHOOD_PASS)
