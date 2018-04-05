#!/usr/bin/python

import os.path
import time
import sys
import sqlite3
from datetime import datetime, timedelta
from pypika import Query, Table, Field, Order
from trader.strategy import *
from datetime import datetime, timedelta
import threading
import sys
from trader.WebHandler import WebThread
from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.AccountBinance import AccountBinance
from config import *

def simulate(conn, client):
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker ORDER BY t ASC")

    assets_info = get_info_all_assets(client)
    balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    accnt = AccountBinance(client, simulation=True)
    accnt.update_asset_balance('BTC', 0.06, 0.06)
    multitrader = MultiTrader(client, 'momentum_swing_strategy', assets_info=assets_info, volumes=None, simulate=True, accnt=accnt)
    #row = None

    print(multitrader.accnt.balances)

    tickers = {}

    found = False

    for row in c:
        msg = {'t': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        tickers[msg['s']] = float(msg['c'])
        if msg['s'] == 'BTCUSDT' and not found:
            found = True
            total_btc = multitrader.accnt.balances['BTC']['balance']
            total_usd = float(msg['o']) * total_btc
            print("Initial BTC={}".format(total_btc))

        #print(msg)
        multitrader.process_message(msg)

    print(multitrader.accnt.balances)
    print("Final BTC={}".format(multitrader.accnt.get_total_btc_value(tickers=tickers)))
    # calculate what the earnings would be for buy and hold:
    #amount = initial_balance_usd / first_buy_price
    #final_balance_usd = amount * last_sell_price
    #print("Buy and hold results:")
    #print("\tInitial balance USD={}".format(initial_balance_usd))
    #print("\tFinal balance USD={}".format(round(final_balance_usd, 2)))
    #total = strategy.accnt.market_price * strategy.accnt.balance + strategy.accnt.quote_currency_balance
    #print("scotts_smma results:")
    #print("\tInitial balance USD={}".format(initial_balance_usd))
    #print("\tFinal balance USD={}".format(total))

def get_info_all_assets(client):
    assets = {}
    for key, value in client.get_exchange_info().items():
        if key != 'symbols':
            continue
        for asset in value:
            minQty = ''
            tickSize = ''
            for filter in asset['filters']:
                if 'minQty' in filter:
                    minQty = filter['minQty']
                if 'tickSize' in filter:
                    tickSize = filter['tickSize']
            assets[asset['symbol']] = {'minQty': minQty,'tickSize': tickSize}
    return assets

def get_asset_balances(client):
    balances = {}
    for accnt in client.get_account()['balances']:
        if float(accnt['free']) == 0.0 and float(accnt['locked']) == 0.0:
            continue

        balances[accnt['asset']] = float(accnt['free']) + float(accnt['locked'])
    return balances

def filter_assets_by_minqty(assets_info, balances):
    currencies = ['BTC', 'ETH', 'BNB']
    result = {}
    for name, balance in balances.items():
        for currency in currencies:
            symbol = "{}{}".format(name, currency)
            if symbol not in assets_info.keys(): continue

            minQty = float(assets_info[symbol]['minQty'])
            if float(balance) >= minQty:
                result[name] = balance
    return result

if __name__ == '__main__':
    client = Client(MY_API_KEY, MY_API_SECRET)
    conn = sqlite3.connect('cryptocurrency_database.miniticker_collection_04032018.db')

    # start the Web API
    #thread = threading.Thread(target=WebThread, args=(strategy,))
    #thread.daemon = True
    #thread.start()

    simulate(conn, client)
    conn.close()
