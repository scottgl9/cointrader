#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import sqlite3
import json
import os
from datetime import datetime
import sys
import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from trader.indicator.EMA import EMA
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Kline import Kline

from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import argparse
import logging


def simulate(conn, client, strategy, logger):
    c = conn.cursor()
    c.execute("SELECT * FROM miniticker ORDER BY E ASC")

    assets_info = get_info_all_assets(client)
    #balances = filter_assets_by_minqty(assets_info, get_asset_balances(client))
    accnt = AccountBinance(client, simulation=True)
    accnt.update_asset_balance('BTC', 0.06, 0.06)
    #accnt.update_asset_balance('ETH', 0.1, 0.1)
    #accnt.update_asset_balance('BNB', 15.0, 15.0)

    multitrader = MultiTrader(client,
                              strategy,
                              assets_info=assets_info,
                              volumes=None,
                              simulate=True,
                              accnt=accnt,
                              logger=logger,
                              store_trades=True)

    print(multitrader.accnt.balances)

    tickers = {}

    found = False

    initial_btc_total = 0.0

    first_ts = None
    last_ts = None

    for row in c:
        msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3],
               'o': row[4], 'q': row[5], 's': row[6], 'v': row[7]}
        tickers[msg['s']] = float(msg['c'])
        if not first_ts:
            first_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        else:
            last_ts = datetime.utcfromtimestamp(int(msg['E'])/1000)
        if msg['s'] == 'BTCUSDT' and not found:
            if multitrader.accnt.total_btc_available(tickers):
                found = True
                #total_btc = multitrader.accnt.balances['BTC']['balance']
                total_btc = multitrader.accnt.get_total_btc_value(tickers)
                initial_btc_total = total_btc
                total_usd = float(msg['o']) * total_btc
                print("Initial BTC={}".format(total_btc))

        multitrader.update_tickers(tickers)

        kline = Kline(symbol=msg['s'],
                      open=float(msg['o']),
                      close=float(msg['c']),
                      low=float(msg['l']),
                      high=float(msg['h']),
                      volume=float(msg['v']),
                      ts=int(msg['E']))

        multitrader.process_message(kline)

    # total_time_hours = (last_ts - first_ts).total_seconds() / (60 * 60)
    # print("total time (hours): {}".format(round(total_time_hours, 2)))
    #
    # print(multitrader.accnt.balances)
    # final_btc_total = multitrader.accnt.get_total_btc_value(tickers=tickers)
    # pprofit = round(100.0 * (final_btc_total - initial_btc_total) / initial_btc_total, 2)
    # print("Final BTC={} profit={}%".format(multitrader.accnt.get_total_btc_value(tickers=tickers), pprofit))
    # for pair in multitrader.trade_pairs.values():
    #     for signal in pair.strategy.get_signals():
    #         if signal.buy_price != 0.0:
    #             buy_price = float(signal.buy_price)
    #             last_price = float(pair.strategy.last_price)
    #             symbol = pair.strategy.ticker_id
    #             pprofit = round(100.0 * (last_price - buy_price) / buy_price, 2)
    #             print("{} ({}): {}%".format(symbol, signal.id, pprofit))

    return multitrader.get_stored_trades()

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

class TabType:
    def __init__(self, name):
        self.name = name
        self.tab = None
        self.figure = None
        self.canvas = None

class mainWindow(QtGui.QTabWidget):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.tabs = {}

    def process(self, conn, trades):
        symbols=trades.keys()
        c = conn.cursor()
        for s in symbols:
            data = []
            c.execute("SELECT c FROM miniticker WHERE s='{}' ORDER BY E ASC".format(s))
            for row in c:
                data.append(float(row[0]))
            self.create_tab(s)
            self.plot_tab(s, data, trades[s])

    def create_tab(self, name):
        tabtype = TabType(name)
        tabtype.tab = QtGui.QWidget()
        self.addTab(tabtype.tab, name)
        tabtype.figure = plt.figure(figsize=(10,5))
        tabtype.canvas = FigureCanvas(tabtype.figure)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabtype.canvas)
        tabtype.tab.setLayout(layout)
        self.tabs[name] = tabtype

    def plot_tab(self, name, data=None, trades=None):
        ax = self.tabs[name].figure.add_subplot(211)
        for trade in trades:
            if trade['type'] == 'buy':
                ax.axvline(x=trade['index'], color='green')
            elif trade['type'] == 'sell':
                ax.axvline(x=trade['index'], color='red')
        ax.plot(data)
        dtwma = DTWMA(window=30)
        #ema26 = EMA(26, scale=24)
        #rsi = RSI(window=30, smoother=ema26)
        #rsi_values = []
        #ema100 = EMA(100, scale=24)
        #ema100_prices = []
        prices = []
        #detector = PeakValleyDetect()
        i=0
        #for (price, ts) in data:
        #    prices.append(float(price))
        #    i+=1
        #ax.plot(prices)
        #ax2 = self.tabs[name].figure.add_subplot(212)
        #ax2.plot(rsi_values)
        self.tabs[name].canvas.draw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='hybrid_signal_market_strategy',
                        help='name of strategy to use')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    #fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "simulate"))
    #fileHandler.setFormatter(logFormatter)
    #logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    client = Client(MY_API_KEY, MY_API_SECRET)
    conn = sqlite3.connect(results.filename)

    # start the Web API
    #thread = threading.Thread(target=WebThread, args=(strategy,))
    #thread.daemon = True
    #thread.start()

    logger.info("Running simulate with {}".format(results.filename))

    trade_cache_filename = str(results.filename).replace('.db', '.txt')
    if not os.path.exists(trade_cache_filename):
        try:
            trades = simulate(conn, client, results.strategy, logger)
        except (KeyboardInterrupt, SystemExit):
            logger.info("CTRL+C: Exiting....")
            conn.close()
            sys.exit(0)

        logger.info("Writing trade cache to {}".format(trade_cache_filename))
        with open(trade_cache_filename, "w") as f:
            f.write(json.dumps(trades))
    else:
        logger.info("Loading {}".format(trade_cache_filename))
        with open(trade_cache_filename, "r") as f:
            trades = json.loads(str(f.read()))

    for key, value in trades.items():
        if str(key).endswith("BNB"):
            del trades[key]

    logger.info("Plotting results...")
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.process(conn, trades)
    main.show()
    sys.exit(app.exec_())

