#!/usr/bin/python

from trader.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from config import *

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, 'BNB', 'BTC')
    print(accnt.get_account_balance())
    print(accnt.get_orders())
    print(accnt.get_fills())
    print(accnt.get_deposit_address())
    print(accnt.html_run_stats())
    #print(accnt.get_account_history())
