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
import pandas as pd
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.lib.Crossover2 import Crossover2
from trader.lib.Indicator import Indicator
from trader.indicator.LSMA import LSMA
from trader.indicator.ADL import ADL
from trader.indicator.ATR import ATR
from trader.indicator.DELTA import DELTA
from trader.indicator.EFI import EFI
from trader.indicator.EMA import EMA
from trader.indicator.KST import KST
from trader.indicator.MACD import MACD
from trader.indicator.McGinleyDynamic import McGinleyDynamic
from trader.indicator.OBV import OBV
from trader.indicator.PPO import PPO
from trader.indicator.ROC import ROC
from trader.indicator.RSI import RSI
from trader.indicator.TSI import TSI

from numpy import hstack
from numpy import insert
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.utils import to_categorical
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


def process_raw_klines(df, indicators=None):
    # process EMA close values
    indicator_close = Indicator(EMA, 12) #McGinleyDynamic, 14, k=1.0)
    if indicators:
        indicator_close_indicator = indicators['CLOSE']
        indicator_close.set_indicator(indicator_close_indicator)
    indicator_close.load_dataframe(df)
    df['CLOSE'] = np.array(indicator_close.results())
    indicator_close_indicator = indicator_close.indicator

    if not indicators:
        indicators = {}
    indicators['CLOSE'] = indicator_close_indicator

    return df, indicators


def create_labels(df, indicators=None):
    df_result = pd.DataFrame()
    # process ROC values
    delta = Indicator(DELTA, window=2) #, scale=12)
    delta.close_key = "CLOSE"
    try:
        delta_indicator = indicators['DELTA']
        delta.set_indicator(delta_indicator)
    except KeyError:
        pass
    delta.load_dataframe(df)
    df_result['DELTA'] = np.array(delta.results())
    indicator_delta = delta.indicator
    indicators['DELTA'] = indicator_delta
    return df_result, indicators


def create_features(df, indicators=None):
    df_result = pd.DataFrame()

    # process MACD values
    lsma = Indicator(LSMA, 12)
    lsma.close_key = "close"
    try:
        lsma_indicator = indicators['LSMA']
        lsma.set_indicator(lsma_indicator)
    except KeyError:
        pass
    lsma.load_dataframe(df)
    df_result['LSMA'] = np.array(lsma.results())
    indicator_lsma = lsma.indicator

    if not indicators:
        indicators = {}
    indicators['LSMA'] = indicator_lsma

    df_result = df_result.dropna()

    return df_result, indicators

def convert_features_to_dataset(df):
    train_sets = []
    for column in df.columns:
        in_seq = df[column].values
        in_seq = in_seq.reshape((len(in_seq), 1))
        train_sets.append(in_seq)
    dataset = hstack(tuple(train_sets))
    return dataset

def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df_train, indicators = create_features(df, indicators)
    #df_train = df_train.drop(columns="CLOSE")
    df_labels, indicators = create_labels(df, indicators)
    train_label_values = df_labels['DELTA'].values[:df_train.count().iloc[0]]
    dataset = df_train.values
    xscaler = MinMaxScaler(feature_range=(0, 1))
    yscaler = MinMaxScaler(feature_range=(0, 1))
    trainX = xscaler.fit_transform(dataset)
    trainY = yscaler.fit_transform(train_label_values.reshape(-1, 1))

    # define generator
    n_features = trainX.shape[1]
    n_input = 8
    generator = TimeseriesGenerator(trainX, trainY, length=n_input, batch_size=n_input)
    #last_generated, _ = generator[len(generator) - 1]
    #print(last_generated[0][-1])
    #for i in range(len(generator)):
    #    x, y = generator[i]
    #    print('{}'.format(x))

    model = Sequential()
    model.add(LSTM(250, activation='relu', return_sequences=False, input_shape=(n_input, n_features)))
    model.add(Dropout(0.2))
    #model.add(LSTM(units=50, input_shape=(n_input, n_features))) #, return_sequences=True))
    #model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)

    y_act = []
    y_pred = []
    prices = []
    ts = test_start_ts
    while ts <= test_end_ts:
        start_ts = ts
        end_ts = ts + 1000 * 3600 * (n_input - 1)
        df2 = hkdb.get_pandas_klines(symbol, start_ts, end_ts)
        test_df, indicators = create_features(df2, indicators)
        test_labels_df, indicators = create_labels(df2, indicators)
        if test_labels_df['DELTA'].size:
            y_act.append(test_labels_df['DELTA'].values[-1])
        if df2['close'].size:
            prices.append(df2['close'].values[-1])
       # test_df = test_df.drop(columns="CLOSE")
        try:
            test_dataset = np.array([xscaler.transform(test_df.values)])
            prediction = yscaler.inverse_transform(model.predict(test_dataset))
            y_pred.append(prediction[0][0])
        except ValueError:
            pass
        ts += 1000 * 3600

    plt.subplot(211)
    #for i in crossups:
    #    plt.axvline(x=i, color='green')
    #for i in crossdowns:
    #    plt.axvline(x=i, color='red')
    fig1, = plt.plot(prices, label=symbol)
    plt.legend(handles=[fig1])
    plt.subplot(212)
    fig21, = plt.plot(y_act, label='act')
    fig22, = plt.plot(y_pred, label='pred')
    plt.legend(handles=[fig21, fig22])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-p', action='store', dest='split_percent',
                        default='70',
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