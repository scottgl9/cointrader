#!/usr/bin/python

from trader.AccountBinance import AccountBinance
from trader.account.binance.client import Client
from trader.account.binance.exceptions import BinanceAPIException
from config import *

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    accnt = AccountBinance(client, 'BNB', 'BTC')
    balances = accnt.get_account_balances()
    currencies = ['BTC', 'ETH', 'BNB']
    for base_name, info in balances.items():
        funds_available = 0.0
        if 'available' in info:
            funds_available = info['available']
        if base_name == 'BTC': continue
        if base_name == 'ETH': continue
        if base_name == 'BNB': continue
        for currency in currencies:
            ticker_id = "{}{}".format(base_name, currency)
            try:
                for trade in client.get_my_trades(symbol=ticker_id):
                    price = trade['price']

            except BinanceAPIException:
                continue
    #print(accnt.get_orders())
    print(client.get_open_orders())
    print(accnt.get_fills())
    print(accnt.get_deposit_address())
    print(accnt.html_run_stats())
    print(accnt.get_klines())
    #print(accnt.get_account_history())
