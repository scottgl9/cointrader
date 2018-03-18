#!/usr/bin/python

from trader.account.whaleclub import Client
from config import *

if __name__ == '__main__':
    client = Client(api_token=WC_BTC_DEMO_API_KEY)
    print(client.get_active_contracts())
    print(client.get_balance())
    print(client.get_all_markets())
    #accnt = AccountBinance(client, 'BNB', 'BTC')
    #print(accnt.get_account_balance())
    ##print(accnt.get_orders())
    #print(accnt.get_fills())
    #print(accnt.get_deposit_address())
    #print(accnt.html_run_stats())
    #print(accnt.get_account_history())
