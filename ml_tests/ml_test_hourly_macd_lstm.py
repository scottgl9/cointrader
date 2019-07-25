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

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import time
import numpy as np
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD
from numpy import hstack
from numpy import insert
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.utils import to_categorical
from sklearn.preprocessing import MinMaxScaler


def create_labels(ema_values, timestamps, cross_up_timestamps, cross_down_timestamps):
    # get rid of last cross up
    if len(cross_up_timestamps) > len(cross_down_timestamps):
        len_diff = len(cross_down_timestamps) - len(cross_up_timestamps)
        cross_up_timestamps = cross_up_timestamps[:len_diff]

    labels = []
    last_label_index = 0
    offset = 4

    for i in range(0, len(cross_up_timestamps)):
        cross_up_ts = cross_up_timestamps[i]
        cross_down_ts = cross_down_timestamps[i]
        cross_up_index = list(timestamps).index(cross_up_ts)
        cross_down_index = list(timestamps).index(cross_down_ts)

        cross_up_value = ema_values[cross_up_index]
        cross_down_value = ema_values[cross_down_index]
        pchange = 100.0 * (cross_down_value - cross_up_value) / cross_up_value
        if pchange <= 1.0:
            continue
        for i in range(last_label_index, cross_down_index + 1):
            if cross_up_index - offset <= i <= cross_up_index + offset:
                labels.append(2)
            elif cross_down_index - offset <= i <= cross_down_index + offset:
                labels.append(1)
            else:
                labels.append(0)
        last_label_index = cross_down_index + 1
    for i in range(last_label_index, len(ema_values)):
        labels.append(0)
    return labels

def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    cross = Crossover2()
    crossups = []
    crossdowns = []
    cross_up_timestamps = []
    cross_down_timestamps = []
    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    macd = MACD(short_weight=12.0, long_weight=26.0, signal_weight=9.0, scale=1.0)
    ema = EMA(12, scale=24)
    train_ema_values = []
    train_macd_values = []
    train_macd_signal_values = []
    last_cross_type = 0

    i = 0
    train_close_values = df['close'].values
    train_timestamps = df['ts'].values
    for close in train_close_values:
        ema.update(close)
        train_ema_values.append(ema.result)
        macd.update(close)
        cross.update(macd.result, macd.signal.result)
        if cross.crossup_detected() and last_cross_type != 1:
            ts = train_timestamps[i]
            crossups.append(i)
            cross_up_timestamps.append(ts)
            last_cross_type = 1
        if cross.crossdown_detected() and last_cross_type != -1:
            ts = train_timestamps[i]
            crossdowns.append(i)
            cross_down_timestamps.append(ts)
            last_cross_type = -1
        train_macd_values.append(macd.result)
        train_macd_signal_values.append(macd.signal.result)
        i += 1

    labels = create_labels(train_ema_values, train_timestamps, cross_up_timestamps, cross_down_timestamps)

    scaler = MinMaxScaler(feature_range=(0, 1))

    in_seq1 = np.array(train_macd_values)
    in_seq2 = np.array(train_macd_signal_values)
    in_seq1 = in_seq1.reshape((len(in_seq1), 1))
    in_seq2 = in_seq2.reshape((len(in_seq2), 1))
    in_seq1 = scaler.fit_transform(in_seq1)
    in_seq2 = scaler.fit_transform(in_seq2)

    dataset = hstack((in_seq1, in_seq2))

    out_seq = np.array(labels)
    out_seq = to_categorical(out_seq.reshape((len(out_seq), 1)))
    # define generator
    n_features = dataset.shape[1]
    n_input = 4
    n_outputs = out_seq.shape[1]
    generator = TimeseriesGenerator(dataset, out_seq, length=n_input, batch_size=8)
    # define model
    model = Sequential()
    model.add(LSTM(100, input_shape=(n_input, n_features)))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)
    column_count = 3

    df_test = hkdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    test_close_values = df_test['close'].values
    test_timestamps = df_test['ts'].values
    test_ema_values = []
    test_macd_values = []
    test_macd_signal_values = []
    for close in test_close_values:
        ema.update(close)
        test_ema_values.append(ema.result)
        macd.update(close)
        test_macd_values.append(macd.result)
        test_macd_signal_values.append(macd.signal.result)

    in_seq1 = np.array(test_macd_values)
    in_seq2 = np.array(test_macd_signal_values)
    in_seq1 = in_seq1.reshape((len(in_seq1), 1))
    in_seq2 = in_seq2.reshape((len(in_seq2), 1))
    in_seq1 = scaler.fit_transform(in_seq1)
    in_seq2 = scaler.fit_transform(in_seq2)

    in_seq1_df = mlhelper.series_to_supervised(in_seq1, n_input, 0)
    in_seq2_df = mlhelper.series_to_supervised(in_seq2, n_input, 0)
    print(in_seq1_df.count().iloc[0])
    for i in range(0, in_seq1_df.count().iloc[0]):
        values1 = in_seq1_df.iloc[i].values
        values2 = in_seq2_df.iloc[i].values
        values1 = values1.reshape((len(values1), 1))
        values2 = values2.reshape((len(values2), 1))
        test_dataset = hstack((values1, values2)).reshape((1, n_input, n_features))
        print(model.predict(test_dataset, batch_size=1))

    plt.subplot(211)
    #for i in crossups:
    #    plt.axvline(x=i, color='green')
    #for i in crossdowns:
    #    plt.axvline(x=i, color='red')
    fig1, = plt.plot(test_close_values, label=symbol)
    fig2, = plt.plot(test_ema_values, label="EMA12")
    plt.legend(handles=[fig1, fig2])
    plt.subplot(212)
    fig1, = plt.plot(test_macd_values, label='MACD')
    fig2, = plt.plot(test_macd_signal_values, label='MACD_SIGNAL')
    plt.legend(handles=[fig1, fig2])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
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

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = HourlyKlinesDB(accnt, results.hourly_filename, None)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = hkdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = hkdb.get_table_start_ts(results.symbol)
    train_end_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index)
    test_start_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index + 1)
    test_end_ts = hkdb.get_table_end_ts(results.symbol)

    if results.symbol:
        simulate(hkdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
    else:
        parser.print_help()
    hkdb.close()
