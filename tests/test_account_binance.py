#!/usr/bin/python

from trader.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from config import *

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, 'BNB', 'BTC')
    print(accnt.get_account_balance())