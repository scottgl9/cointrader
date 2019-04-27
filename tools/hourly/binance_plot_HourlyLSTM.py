#!/usr/bin/python
# test HourlyLSTM class

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
import time
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance

from trader.indicator.OBV import OBV
try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential, load_model
from sklearn.cross_validation import  train_test_split
from sklearn.preprocessing import MinMaxScaler
import talib
from trader.indicator.RSI import RSI
from trader.indicator.MACD import MACD
from trader.indicator.LSMA import LSMA
from trader.lib.Indicator import Indicator


# convert an array of values into a dataset matrix
def create_dataset(dataset, x_scaler, y_scaler, column='close'):
    dataX = dataset.shift(1).dropna().values
    dataY = dataset[column].shift(-1).dropna().values

    #if len(dataY) > len(dataX):
    #    dataY = dataY[:len(dataX)]

    dataY = dataY.reshape(-1, 1)

    scaleX = x_scaler.fit_transform(dataX)
    scaleY = y_scaler.fit_transform(dataY)
    return np.array(scaleX), np.array(scaleY)


# get index of column name
def get_index_column(dataset, column='close'):
    # get column names
    names = list(dataset)
    # get index of column before scaling
    column_index = names.index(column)
    return column_index

def create_model(columns=3, rows=1, batch_size=32, model=None):
    new_model = Sequential()

    new_model.add(LSTM(units=50, return_sequences=True, batch_input_shape=(batch_size, columns, rows)))
    new_model.add(Dropout(0.2))

    new_model.add(LSTM(units=50, return_sequences=True))
    new_model.add(Dropout(0.2))

    new_model.add(LSTM(units=50, return_sequences=True))
    new_model.add(Dropout(0.2))

    new_model.add(LSTM(units=50))
    new_model.add(Dropout(0.2))

    new_model.add(Dense(units=1))

    #for reshaping batch_size from a previously created model
    if model:
        weights = model.get_weights()
        new_model.set_weights(weights)

    new_model.compile(optimizer='adam', loss='mean_squared_error')
    return new_model


def train_model(symbol, X_train, Y_train, epoch=50, batch_size=32):
    filename = "models/{}.h5".format(symbol)
    if os.path.exists(filename):
        model = load_model(filename)
        return model

    model = create_model(columns=X_train.shape[1], rows=X_train.shape[2], batch_size=batch_size)
    for i in range(epoch):
        model.fit(X_train, Y_train, epochs=1, batch_size=batch_size)
    model.save(filename)
    return model


def simulate(hkdb, symbol, start_ts, end_ts):
    hourly_lstm = HourlyLSTM(hkdb, symbol)

    hourly_lstm.load(start_ts=0, end_ts=start_ts)

    testy = []
    predicty = []

    count = 0

    ts = start_ts + 3600 * 1000
    while count <= 1000: #ts <= end_ts:
        #print(time.ctime(int(ts / 1000)))
        hourly_lstm.update(ts)
        testy.append(hourly_lstm.test_result)
        predicty.append(hourly_lstm.predict_result)
        ts += 3600 * 1000
        count += 1

    # plot_predict_y = []
    # for X in testX:
    #     Y = test_model.predict(np.array( [X,] ))
    #     predictY = y_scaler.inverse_transform(Y)
    #     plot_predict_y.append(predictY[0][0])
    #
    # plot_test_y = y_scaler.inverse_transform(testY).reshape(1, -1)[0]
    #
    plt.subplot(211)
    fig1, = plt.plot(testy, label='TESTY')
    fig2, = plt.plot(predicty, label='PREDICTY')
    plt.legend(handles=[fig1, fig2])
    plt.show()

# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

def get_last_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # used to get first timestamp for symbol from precaptured live market data
    parser.add_argument('-f', action='store', dest='filename',
                        default='cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    results = parser.parse_args()


    hourly_filename = results.hourly_filename
    symbol = results.symbol
    start_ts = 0
    end_ts = 0

    accnt = AccountBinance(None, simulation=True, simulate_db_filename=results.filename)

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            start_ts = get_first_timestamp(results.filename, symbol)
            end_ts = get_last_timestamp(hourly_filename, symbol)
            start_ts = accnt.get_hourly_ts(start_ts)
            print(start_ts, end_ts)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = HourlyKlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    hkdb.close()
