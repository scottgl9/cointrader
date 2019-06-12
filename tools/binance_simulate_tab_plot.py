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
                msg = {'E': row[0], 'c': row[1], 'h': row[2], 'l': row[3], 'q': row[5], 'v': row[7]}
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
        ax = self.tabs[name].figure.add_subplot(211)
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
        ax3 = self.tabs[name].figure.add_subplot(212)
        ax3.plot(volumes_quote)
        #ax3.plot(obv_ema12_values)
        #ax3.plot(obv_ema26_values)
        #ax3.plot(obv_ema100_values)
        self.tabs[name].canvas.draw()

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

    logger.info("Plotting results...")
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.process(conn, trades)
    main.show()
    sys.exit(app.exec_())
