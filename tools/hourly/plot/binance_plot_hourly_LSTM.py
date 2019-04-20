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
import talib


# convert an array of values into a dataset matrix
def create_dataset(dataset, column='close'):
    dataX, dataY = [], []
    # get column names
    names = list(dataset)
    # get index of column before scaling
    column_index = names.index(column)

    # scale dataset
    sc = MinMaxScaler(feature_range = (0, 1))
    sdataset = sc.fit_transform(dataset)

    for i in range(len(sdataset)-1):
        #dataY.append(dataset[column][i+1])
        #dataX.append(dataset.iloc[i].values)
        dataX.append(sdataset[i])
        dataY.append(sdataset[i+1][column_index])
    return np.array(dataX), np.array(dataY)


def train_model(symbol, X_train, Y_train):
    filename = "models/{}.h5".format(symbol)
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

    #if os.path.exists(filename):

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X_train, Y_train, epochs=50, batch_size=32)
    model.save(filename)


def simulate(hkdb, symbol, start_ts, end_ts):
    df = hkdb.get_pandas_klines(symbol)
    # remove ts columns from input data
    #df = df.drop(columns=['ts', 'base_volume', 'quote_volume'])

    df['H-L'] = df['high'] - df['low']
    df['C-O'] = df['close'] - df['open']

    df = pd.DataFrame(df, columns=['close', 'H-L', 'C-O'])
    print(df)
    train_size = int(len(df) * 0.80)
    test_size = len(df) - train_size
    train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]
    trainX, trainY = create_dataset(train)
    testX, testY = create_dataset(test)

    #trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    #testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    # reshape for training
    trainX = np.reshape(trainX, (-1, 3, 1))

    train_model(symbol, trainX, trainY)

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

# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # used to get first timestamp for symbol from precaptured live market data
    parser.add_argument('-f', action='store', dest='filename',
                        default='', #'cryptocurrency_database.miniticker_collection_04092018.db',
                        help='filename of kline sqlite db')

    parser.add_argument('--hours', action='store', dest='hours',
                        default=48,
                        help='Hours before first ts in db specified by -f')

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

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            end_ts = get_first_timestamp(results.filename, symbol)
            start_ts = end_ts - 1000 * 3600 * int(results.hours)
            print(start_ts, end_ts)


    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    hkdb = HourlyKlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    hkdb.close()
