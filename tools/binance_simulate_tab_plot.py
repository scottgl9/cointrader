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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.MACD import MACD
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.indicator.OBV import OBV
from trader.lib.Kline import Kline

from trader.account.binance.client import Client
from trader.MultiTrader import MultiTrader
from trader.account.AccountBinance import AccountBinance
from trader.config import *
import argparse
import logging


def simulate(conn, client, strategy, signal_name, logger):
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
                              signal_names=[signal_name],
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
            c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(s))
            for row in c:
                msg = {'E': row[0], 'c': row[1], 'q': row[5], 'v': row[7]}
                data.append(msg)
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
        ax = self.tabs[name].figure.add_subplot(311)
        for trade in trades:
            if trade['type'] == 'buy':
                ax.axvline(x=trade['index'], color='green')
            elif trade['type'] == 'sell':
                ax.axvline(x=trade['index'], color='red')
        prices = []
        ema12 = EMA(12, scale=24)
        ema26 = EMA(26, scale=24)
        ema50 = EMA(50, scale=24)
        ema12_values = []
        ema26_values = []
        ema50_values = []


        dtwma = DTWMA()
        obv = OBV()
        obv_values = []
        obv_ema12 = ZLEMA(12, scale=24)
        obv_ema26 = ZLEMA(26, scale=24)
        obv_ema50 = ZLEMA(50, scale=24)
        obv_ema12_values = []
        obv_ema26_values = []
        obv_ema50_values = []

        macd = MACD(short_weight=12, long_weight=26, signal_weight=20.0, scale=24, plot_mode=True)
        macd_diff_values = []
        macd_signal_values = []

        i=0
        for msg in data:
            price = float(msg['c'])
            ts = msg['E']
            volume = msg['v']
            #print(msg['q'])
            prices.append(price)
            obv.update(price, volume)
            obv_ema12.update(obv.result)
            obv_ema12_values.append(obv_ema12.result)
            obv_ema26.update(obv.result)
            obv_ema26_values.append(obv_ema26.result)
            obv_ema50.update(obv.result)
            obv_ema50_values.append(obv_ema50.result)

            ema12.update(price)
            ema12_values.append(ema12.result)
            ema26.update(price)
            ema26_values.append(ema26.result)
            ema50.update(price)
            ema50_values.append(ema50.result)
            macd.update(price)
            if macd.diff != 0:
                macd_diff_values.append(macd.diff)
            if macd.signal.result != 0:
                macd_signal_values.append(macd.signal.result)
        #    i+=1
        ax.plot(prices)
        ax.plot(ema12_values)
        ax.plot(ema26_values)
        ax.plot(ema50_values)
        ax2 = self.tabs[name].figure.add_subplot(312)
        ax2.plot(macd_diff_values)
        ax2.plot(macd_signal_values)
        ax3 = self.tabs[name].figure.add_subplot(313)
        #ax3.plot(obv_values)
        ax3.plot(obv_ema12_values)
        #ax3.plot(obv_ema26_values)
        ax3.plot(obv_ema50_values)
        self.tabs[name].canvas.draw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-s', action='store', dest='strategy',
                        default='hybrid_signal_market_strategy',
                        help='name of strategy to use')

    parser.add_argument('-g', action='store', dest='signal_name',
                        default='Hybrid_Crossover',
                        help='name of signal to use')
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

    run_simulation = True

    conn = sqlite3.connect(results.filename)
    trade_cache = {}

    trade_cache_name = "{}-{}".format(results.strategy, results.signal_name)

    # if we already ran simulation, load the results
    trade_cache_filename = str(results.filename).replace('.db', '.json')
    if os.path.exists(trade_cache_filename):
        logger.info("Loading {}".format(trade_cache_filename))
        with open(trade_cache_filename, "r") as f:
            trade_cache = json.loads(str(f.read()))

        if trade_cache_name in trade_cache.keys():
            run_simulation = False

    if run_simulation:
        logger.info("Running simulate with {}, strategy {}, signal {}".format(results.filename,
                                                                              results.strategy,
                                                                              results.signal_name))

        try:
            client = Client(MY_API_KEY, MY_API_SECRET)
            trades = simulate(conn, client, results.strategy, results.signal_name, logger)
        except (KeyboardInterrupt, SystemExit):
            logger.info("CTRL+C: Exiting....")
            conn.close()
            sys.exit(0)

        logger.info("Writing trade cache to {}".format(trade_cache_filename))
        with open(trade_cache_filename, "w") as f:
            trade_cache[trade_cache_name] = trades
            f.write(json.dumps(trade_cache))

    plt.rcParams.update({'figure.max_open_warning': 0})

    if not trade_cache or trade_cache_name not in trade_cache.keys():
        logger.error("Failed to load simulation results")
        sys.exit(-1)

    trades = trade_cache[trade_cache_name]

    #for key, value in trades.items():
    #    if str(key).endswith("BNB"):
    #        del trades[key]

    logger.info("Plotting results...")
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.process(conn, trades)
    main.show()
    sys.exit(app.exec_())
