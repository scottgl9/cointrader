#!/usr/bin/env python3# test HourlyLSTM class

import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sys
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.binance.AccountBinance import AccountBinance
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.indicator.LSMA import LSMA
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler


def simulate(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    df = kdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    lsma = LSMA(window=30)
    train_lsma_values = []
    train_close_values = df['close'].values
    train_ts_values = df['ts'].values

    for i in range(0, len(train_close_values)):
        close = train_close_values[i]
        ts = train_ts_values[i]
        lsma.update(close, ts)
        train_lsma_values.append(lsma.result)

    scaler = MinMaxScaler(feature_range=(0, 1))
    train_lsma_values = scaler.fit_transform(np.array(train_lsma_values).reshape(-1, 1))

    df_test = kdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    test_close_values = df_test['close'].values
    test_timestamps = df_test['ts'].values
    test_lsma_values = []
    for i in range(0, len(test_close_values)):
        close = test_close_values[i]
        ts = test_timestamps[i]
        lsma.update(close, ts)
        test_lsma_values.append(lsma.result)
    y_act = test_lsma_values
    test_lsma_values = scaler.transform(np.array(test_lsma_values).reshape(-1, 1))

    # define generator
    n_features = 1
    n_input = 8
    generator = TimeseriesGenerator(train_lsma_values, train_lsma_values, length=n_input, batch_size=32)
    # define model
    model = Sequential()
    model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)
    # make a one step prediction out of sample
    x_input = mlhelper.series_to_supervised(test_lsma_values, n_input, 0).values
    y_pred = []
    for i in range(0, len(x_input)):
        yhat = model.predict(x_input[i].reshape((1, n_input, n_features)), verbose=0)
        yhat = scaler.inverse_transform(yhat)
        y_pred.append(yhat[0][0])

    y_act = y_act[n_input:len(y_pred)+n_input]
    print(len(y_act))
    print(len(y_pred))

    plt.subplot(211)
    #for i in crossups:
    #    plt.axvline(x=i, color='green')
    #for i in crossdowns:
    #    plt.axvline(x=i, color='red')
    fig1, = plt.plot(test_close_values, label=symbol)
    plt.legend(handles=[fig1])
    plt.subplot(212)
    fig21, = plt.plot(y_act, label="LSMA_ACT")
    fig22, = plt.plot(y_pred, label="LSMA_PRED")
    plt.legend(handles=[fig21, fig22])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-p', action='store', dest='split_percent',
                        default='60',
                        help='Percent of klines to use for training (remaining used for test')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    results = parser.parse_args()
    if not results.symbol:
        parser.print_help()
        sys.exit(0)

    accnt = AccountBinance(None, simulate=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    kdb = KlinesDB(accnt, results.hourly_filename, None)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = kdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = kdb.get_table_start_ts(results.symbol)
    train_end_ts = kdb.get_table_ts_by_offset(results.symbol, train_end_index)
    test_start_ts = kdb.get_table_ts_by_offset(results.symbol, train_end_index + 1)
    test_end_ts = kdb.get_table_end_ts(results.symbol)

    if results.symbol:
        simulate(kdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
    else:
        parser.print_help()
    kdb.close()
