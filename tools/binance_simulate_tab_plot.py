#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')

import sqlite3
import json
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from trader.indicator.EMA import EMA
from trader.indicator.AEMA import AEMA
from trader.indicator.OBV import OBV
from trader.lib.MAAvg import MAAvg
from trader.lib.MovingTimeSegment.MTSPriceChannel import MTSPriceChannel
from trader.TraderConfig import TraderConfig

import argparse
import logging

class mainWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.figure = plt.figure(figsize=(10,5))
        self.canvas = FigureCanvas(self.figure)
        layout = QtGui.QVBoxLayout()
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.activated[str].connect(self.change_plot)
        layout.addWidget(self.comboBox)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.trades = None
        self.end_tickers = None
        self.symbols = None
        self.conn = None

    def process(self, conn, trades, end_tickers):
        self.conn = conn
        self.trades = trades
        self.end_tickers = end_tickers
        self.symbols=trades.keys()
        # percent change for each symbol
        self.symbols_percent = {}
        for symbol in self.symbols:
            # trades for a given symbol
            strades = self.trades[symbol]
            percents = []
            # an extra buy without a matching sell
            if (len(strades) & 1) != 0:
                buy_price = strades[-1]['price']
                last_price = end_tickers[symbol]
                percents.append(100.0 * (last_price - buy_price) / buy_price)
                for strade in strades[:-1]:
                    if strade['type'] != 'sell':
                        continue
                    buy_price = float(strade['buy_price'])
                    sell_price = float(strade['price'])
                    percents.append(100.0 * (sell_price - buy_price) / buy_price)
            else:
                for strade in strades:
                    if strade['type'] != 'sell':
                        continue
                    buy_price = float(strade['buy_price'])
                    sell_price = float(strade['price'])
                    percents.append(100.0 * (sell_price - buy_price) / buy_price)
            percent = round(sum(percents), 2)
            self.symbols_percent[symbol] = percent
        first_text = None
        for percent, symbol in sorted((value,key) for (key,value) in self.symbols_percent.items()):
            text = "{}: {}%".format(symbol, percent)
            if not first_text:
                first_text = text
            self.comboBox.addItem(text)

        #self.comboBox.addItems(self.symbols)
        self.change_plot(first_text)

    def change_plot(self, s):
        s = str(s).split(':')[0]
        print(s)
        c = conn.cursor()
        data = []
        c.execute("SELECT * FROM miniticker WHERE s='{}' ORDER BY E ASC".format(s))
        for row in c:
            msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3], 'q': row[5], 'v': row[7]}
            data.append(msg)
        self.figure.clear()
        self.plot(s, data, self.trades[s])

    def plot(self, name, data=None, trades=None):
        prices = []
        high_values = []
        low_values = []
        aema12 = AEMA(12)
        aema26 = AEMA(26)
        aema50 = AEMA(50)
        aema200 = AEMA(200)
        aema12_values = []
        aema26_values = []
        aema50_values = []
        aema200_values = []

        maavg = MAAvg()
        #maavg.add(ema12)
        #maavg.add(ema26)
        #maavg.add(ema50)
        maavg_x_values = []
        maavg_values = []

        obv = OBV()
        volumes_base = []
        volumes_quote = []
        obv_values = []
        obv_ema12 = EMA(12)
        obv_ema26 = EMA(26)
        obv_ema100 = EMA(500)
        obv_ema12_values = []
        obv_ema26_values = []
        obv_ema100_values = []
        tspc = MTSPriceChannel(minutes=60)
        tspc_values = []
        tspc_x_values = []

        i=0
        for msg in data:
            price = float(msg['c'])
            high = float(msg['h'])
            high_values.append(high)
            low = float(msg['l'])
            low_values.append(low)
            ts = msg['E']
            volume_base = float(msg['v'])
            volumes_base.append(volume_base)
            volume_quote = float(msg['q'])
            volumes_quote.append(volume_quote)

            prices.append(price)
            obv.update(price, volume_base)
            obv_values.append(obv.result)
            obv_ema12.update(obv.result)
            obv_ema12_values.append(obv_ema12.result)
            obv_ema26.update(obv.result)
            obv_ema26_values.append(obv_ema26.result)
            obv_ema100.update(obv.result)
            obv_ema100_values.append(obv_ema100.result)

            tspc.update(price, ts)
            if tspc.ready():
                tspc_values.append(tspc.result)
                tspc_x_values.append(i)

            aema12.update(price, ts)
            aema12_values.append(aema12.result)
            aema26.update(price, ts)
            aema26_values.append(aema26.result)
            aema50.update(price, ts)
            aema50_values.append(aema50.result)
            aema200.update(price, ts)
            aema200_values.append(aema200.result)

            maavg.update()
            if maavg.result:
                maavg_values.append(maavg.result)
                maavg_x_values.append(i)

            i += 1


        handles = []
        ax = self.figure.add_subplot(211)
        for trade in trades:
            if trade['type'] == 'buy':
                handles.append(ax.axvline(x=trade['index'], color='green', label="BUY_{}".format(trade['trade_type'])))
            elif trade['type'] == 'sell':
                handles.append(ax.axvline(x=trade['index'], color='red', label="SELL_{}".format(trade['trade_type'])))
        fig1, = ax.plot(prices, label=name)
        fig2, = ax.plot(tspc_x_values, tspc_values, label="TPSC")
        fig3, = ax.plot(aema12_values, label="AEMA12")
        fig4, = ax.plot(aema26_values, label="AEMA26")
        fig5, = ax.plot(aema50_values, label="AEMA50")
        fig6, = ax.plot(maavg_x_values, maavg_values, label="MAAVG")
        fig7, = ax.plot(aema200_values, label="AEMA200")
        #fig8, = ax.plot(low_values, label="low")
        #fig9, = ax.plot(high_values, label="high")
        for f in [fig1, fig2, fig3, fig4, fig5, fig6, fig7]:
            handles.append(f)
        ax.legend(handles=handles)
        #ax2 = self.tabs[name].figure.add_subplot(312)
        #ax2.plot(macd_diff_values)
        #ax2.plot(macd_signal_values)
        ax3 = self.figure.add_subplot(212)
        ax3.plot(volumes_quote)
        #ax3.plot(obv_ema12_values)
        #ax3.plot(obv_ema26_values)
        #ax3.plot(obv_ema100_values)
        self.canvas.draw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-c', action='store', dest='cache_dir',
                        default='cache',
                        help='simulation cache directory')

    results = parser.parse_args()

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    config = TraderConfig("trader.ini")
    config.select_section('binance.simulate')
    strategy = config.get('strategy')
    signal_name = config.get('signals')

    if not os.path.exists(results.cache_dir):
        logger.warning("cache directory {} doesn't exist, exiting...".format(results.cache_dir))
        sys.exit(0)

    conn = sqlite3.connect(results.filename)
    trade_cache = {}

    trade_cache_name = "{}-{}".format(strategy, signal_name)

    # if we already ran simulation, load the results
    trade_cache_filename = os.path.join(results.cache_dir, results.filename.replace('.db', '.json'))
    if os.path.exists(trade_cache_filename):
        logger.info("Loading {} from {}".format(trade_cache_name, trade_cache_filename))
        with open(trade_cache_filename, "r") as f:
            trade_cache = json.loads(str(f.read()))

        if trade_cache_name not in trade_cache.keys():
            logger.error("Failed to load {}, exiting...".format(trade_cache_name))
            sys.exit(-1)

    plt.rcParams.update({'figure.max_open_warning': 0})

    if not trade_cache or trade_cache_name not in trade_cache.keys():
        logger.error("Failed to load simulation results")
        sys.exit(-1)

    trades = trade_cache[trade_cache_name]['trades']
    end_tickers = trade_cache['end_tickers']

    logger.info("Plotting results...")
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.showMaximized()
    main.process(conn, trades, end_tickers)
    main.show()
    sys.exit(app.exec_())
