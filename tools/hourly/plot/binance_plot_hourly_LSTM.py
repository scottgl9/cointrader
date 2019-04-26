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


def train_model(symbol, X_train, Y_train, epoch=50, batch_size=32):
    filename = "models/{}.h5".format(symbol)
    if os.path.exists(filename):
        model = load_model(filename)
        return model

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

    model.fit(X_train, Y_train, epochs=epoch, batch_size=batch_size)
    model.save(filename)
    return model


def simulate(hkdb, symbol, start_ts, end_ts):
    df = hkdb.get_pandas_klines(symbol)
    # remove ts columns from input data
    #df = df.drop(columns=['ts', 'base_volume', 'quote_volume'])

    # process LSMA close values
    lsma_close = Indicator(LSMA, 12)
    lsma_close.load_dataframe(df)
    df['LSMA_CLOSE'] = np.array(lsma_close.results())

    # process OBV values
    obv = Indicator(OBV)
    obv.volume_key = 'quote_volume'
    #obv.close_key='LSMA_CLOSE'
    obv.load_dataframe(df)
    df['OBV'] = np.array(obv.results())

    # process RSI values
    rsi = Indicator(RSI, 14)
    #rsi.close_key = 'LSMA_CLOSE'
    rsi.load_dataframe(df)
    rsi_result = np.array(rsi.results())
    rsi_result[rsi_result == 0] = np.nan
    df['RSI'] = rsi_result
    print(df['RSI'].values.tolist()[:100])
    df['RSI12'] = talib.RSI(df['close'].values, timeperiod=14)
    print(df['RSI12'].values.tolist()[:100])

    columns = ['LSMA_CLOSE', 'RSI', 'OBV']

    df = pd.DataFrame(df, columns=columns)
    df = df.dropna()

    # scale dataset
    x_scaler = MinMaxScaler(feature_range = (0, 1))
    y_scaler = MinMaxScaler(feature_range = (0, 1))

    train_size = int(len(df) * 0.80)
    test_size = len(df) - train_size
    train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]

    trainX, trainY = create_dataset(train, x_scaler, y_scaler, column='LSMA_CLOSE')
    testX, testY = create_dataset(test, x_scaler, y_scaler, column='LSMA_CLOSE')

    # reshape for training
    trainX = np.reshape(trainX, (-1, len(columns), 1))

    model = train_model(symbol, trainX, trainY, epoch=15)

    testX = np.reshape(testX, (-1, len(columns), 1))
    predictY = model.predict(testX)
    predictY = y_scaler.inverse_transform(predictY)
    scores = model.evaluate(testX, testY, verbose=0)
    print(scores)

    plot_predict_y = predictY.reshape(1, -1)[0]
    plot_test_y = y_scaler.inverse_transform(testY).reshape(1, -1)[0]

    #print(plot_predict_y)
    #print(plot_test_y)

    #train_close_values = y_scaler.inverse_transform(trainY).reshape(1, -1)[0]
    #compute_real_predict(model, close_values=train_close_values, count=test_size, x_scaler=x_scaler, y_scaler=y_scaler)

    plt.subplot(211)
    fig1, = plt.plot(plot_test_y, label='TESTY')
    fig2, = plt.plot(plot_predict_y, label='PREDICTY')
    plt.legend(handles=[fig1, fig2])
    plt.show()

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
