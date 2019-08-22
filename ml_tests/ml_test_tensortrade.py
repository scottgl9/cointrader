#!/usr/bin/python3
# Test of tensortrade library https://github.com/notadamking/tensortrade

import sys
import os
import ccxt
import warnings

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.abspath('')))

from tensortrade.environments import TradingEnvironment
from tensortrade.exchanges.live import CCXTExchange

binance = ccxt.binance()

exchange = CCXTExchange(exchange=binance)

exchange.next_observation()

