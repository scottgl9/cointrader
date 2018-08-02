#!/usr/bin/python

#from pymongo import MongoClient
import sys
from trader.AccountGDAX import AccountGDAX
from trader.account.gdax.authenticated_client import AuthenticatedClient
from trader import gdax

from trader.config import *


if __name__ == '__main__':
    auth_client = AuthenticatedClient(GDAX_KEY, GDAX_SECRET, GDAX_PASS)
    accnt = AccountGDAX(auth_client, 'BTC', 'USD')
    for fill in accnt.get_fills()[0]:
        print(fill)
    print("orders:")
    for order in accnt.get_orders():
        print(order)
    print(accnt.get_4hr_stats())
