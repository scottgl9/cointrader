#!/usr/bin/python

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.indicator.OBV import OBV
try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA

import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from sklearn.cross_validation import  train_test_split
from sklearn.preprocessing import MinMaxScaler


# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)


def scale_dataset(training_set):
    sc = MinMaxScaler(feature_range = (0, 1))
    return sc.fit_transform(training_set)


def train_model(X_train, Y_train):
    model = Sequential()

    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))

    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(units=50))
    model.add(Dropout(0.2))

    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X_train, Y_train, epochs=100, batch_size=32)


def simulate(hkdb, symbol):
    df = hkdb.get_pandas_klines(symbol)

    df = scale_dataset(df)

    train_size = int(len(df) * 0.80)
    test_size = len(df) - train_size
    train, test = df[0:train_size, :], df[train_size:len(df), :]
    trainX, trainY = create_dataset(train, look_back=1)
    testX, testY = create_dataset(test, look_back=1)

    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    train_model(trainX, trainY)

    #plt.subplot(211)
    #symprice, = plt.plot(close_prices, label=symbol)
    #fig1, = plt.plot(ema12_values, label='EMA12')
    #fig2, = plt.plot(ema26_values, label='EMA26')
    #fig3, = plt.plot(ema50_values, label='EMA50')
    #fig4, = plt.plot(ema200_values, label='EMA200')
    #plt.legend(handles=[symprice, fig1, fig2, fig3, fig4])
    #plt.subplot(212)
    #fig21, = plt.plot(obv_ema12_values, label='OBV12')
    #fig22, = plt.plot(obv_ema26_values, label='OBV26')
    #fig23, = plt.plot(obv_ema50_values, label='OBV50')
    #plt.legend(handles=[fig21, fig22, fig23])
    #plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    results = parser.parse_args()

    if not os.path.exists(results.filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    filename = results.filename
    symbol = results.symbol

    hkdb = HourlyKlinesDB(None, filename, None)
    print("Loading {}".format(filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol)
    hkdb.close()
