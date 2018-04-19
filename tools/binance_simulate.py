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
    c.execute("SELECT * FROM miniticker ORDER BY E ASC")

    assets_info = get_info_all_assets(client)
    #balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    accnt = AccountBinance(client, simulation=True)
    accnt.update_asset_balance('BTC', 0.06, 0.06)
    #accnt.update_asset_balance('ETH', 0.1, 0.1)
    #accnt.update_asset_balance('BNB', 10.0, 10.0)

    multitrader = MultiTrader(client, 'support_resistance_level_strategy', assets_info=assets_info, volumes=None, simulate=True, accnt=accnt)
    #row = None

    print(multitrader.accnt.balances)

    tickers = {}

    found = False

    initial_btc_total = 0.0

    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        tickers[msg['s']] = float(msg['c'])
        if msg['s'] == 'BTCUSDT' and not found:
            found = True
            total_btc = multitrader.accnt.balances['BTC']['balance']
            initial_btc_total = total_btc
            total_usd = float(msg['o']) * total_btc
            print("Initial BTC={}".format(total_btc))

        #print(msg)
        multitrader.process_message(msg)

    print(multitrader.accnt.balances)
    final_btc_total = multitrader.accnt.get_total_btc_value(tickers=tickers)
    pprofit = round(100.0 * (final_btc_total - initial_btc_total) / initial_btc_total, 2)
    print("Final BTC={} profit={}%".format(multitrader.accnt.get_total_btc_value(tickers=tickers), pprofit))
    for pair in multitrader.trade_pairs.values():
        if pair.strategy.buy_price != 0.0:
            buy_price = float(pair.strategy.buy_price)
            last_price = float(pair.strategy.last_price)
            symbol = pair.strategy.ticker_id
            pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
            print("{}: {}%".format(symbol, pprofit))

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
    currencies = ['BTC', 'ETH', 'BNB', 'USDT']
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
    conn = sqlite3.connect('cryptocurrency_database.miniticker_collection_04092018.db')

    # start the Web API
    #thread = threading.Thread(target=WebThread, args=(strategy,))
    #thread.daemon = True
    #thread.start()

    simulate(conn, client)
    conn.close()
