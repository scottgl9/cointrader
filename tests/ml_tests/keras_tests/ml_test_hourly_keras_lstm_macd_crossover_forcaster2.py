#!/usr/bin/env python3# test HourlyLSTM class

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
from trader.KlinesDB import KlinesDB
from trader.account.AccountBinance import AccountBinance
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.lib.Crossover2 import Crossover2
from trader.lib.Indicator import Indicator
from trader.indicator.LSMA import LSMA
from trader.indicator.ADL import ADL
from trader.indicator.ATR import ATR
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
from keras.layers import TimeDistributed, RepeatVector
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


def create_labels(df_train):
    df_result = pd.DataFrame()
    df_result['MACD'] = df_train['MACD']
    return df_result


def create_features(df, indicators=None):
    df_result = pd.DataFrame()

    # process MACD values
    macd = Indicator(MACD) #, scale=12)
    macd.close_key = "CLOSE"
    try:
        macd_indicator = indicators['MACD']
        macd.set_indicator(macd_indicator)
    except KeyError:
        pass
    macd.load_dataframe(df)
    macd_result = np.array(macd.results(0))
    macd_result[macd_result == 0] = np.nan
    macd_sig_result = np.array(macd.results(1))
    macd_sig_result[macd_sig_result == 0] = np.nan
    df_result['MACD'] = macd_result
    indicator_macd = macd.indicator

    if not indicators:
        indicators = {}
    indicators['MACD'] = indicator_macd

    df_result = df_result.dropna()

    return df_result, indicators


# for training forcasting df_labels[(i + shift)] for df_feats[i]:
# shift df_feats +shift, and shift df_labels -shift
def shift_features_and_labels(df_feats, df_labels, shift=1):
    df_feats = df_feats.iloc[:-shift, :]
    df_labels = df_labels.iloc[shift:, :]

    return df_feats, df_labels


def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    xscaler = MinMaxScaler(feature_range=(0, 1))
    yscaler = MinMaxScaler(feature_range=(0, 1))

    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df, indicators = process_raw_klines(df)
    df_train, indicators = create_features(df, indicators)
    df_labels = create_labels(df_train)
    df_train, df_labels = shift_features_and_labels(df_train, df_labels)

    scaleX = xscaler.fit_transform(df_train.values)
    scaleY = yscaler.fit_transform(df_labels.values)

    #df_train_scaled = mlhelper.convert_np_columns_to_df(scaleX, columns=df_train.columns)
    #df_labels_scaled = mlhelper.convert_np_columns_to_df(scaleY, columns=df_labels.columns)
    #print(df_train_scaled)
    #print(df_labels_scaled)

    # define generator
    n_features = scaleX.shape[1]
    n_input = 4
    n_timesteps = 4
    n_output = scaleY.shape[1]

    generator = TimeseriesGenerator(scaleX, scaleY, length=n_input, batch_size=n_input)
    #print(trainX)
    #print(mlhelper.convert_np_columns_to_df(trainX))
    #print(trainY)
    #print(mlhelper.convert_np_columns_to_df(trainY))
    #last_generated, _ = generator[len(generator) - 1]
    #for i in range(len(generator)):
    #    x, y = generator[i]
    #    print('{}, {}'.format(x, y))

    model = Sequential()
    model.add(LSTM(200, input_shape=(n_input, n_features)))
    model.add(Dropout(0.2))
    #model.add(LSTM(units=50, return_sequences=False, input_shape=(n_input, n_features)))
    #model.add(Dropout(0.2))
    #model.add(TimeDistributed(Dense(100, activation='relu')))
    model.add(Dense(n_output))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)

    y_act = []
    y_act2 = []
    y_pred = []
    y_pred2 = []
    prices = []
    ts = test_start_ts
    while ts <= test_end_ts:
        start_ts = ts
        end_ts = ts + 1000 * 3600 * (n_input - 1)
        df2 = hkdb.get_pandas_klines(symbol, start_ts, end_ts)
        df2, indicators = process_raw_klines(df2, indicators)
        test_df, indicators = create_features(df2, indicators)
        test_labels_df = create_labels(test_df)
        if test_labels_df['MACD'].size:
            y_act.append(test_labels_df['MACD'].values[-1])
        #if test_labels_df['MHIST'].size:
        #    y_act2.append(test_labels_df['MHIST'].values[-1])
        if df2['CLOSE'].size:
            prices.append(df2['CLOSE'].values[-1])
       # test_df = test_df.drop(columns="CLOSE")
        try:
            test_dataset = np.array([xscaler.transform(test_df.values)])
            prediction = yscaler.inverse_transform(model.predict(test_dataset))
            #print(prediction)
            y_pred.append(prediction[0][0])
            #y_pred2.append(prediction[0][1])
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
                        default='binance_hourly_klines_BTC.db',
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


    hkdb = KlinesDB(accnt, results.hourly_filename, None)
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
