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
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD
from trader.indicator.LSMA import LSMA
from trader.indicator.RSI import RSI
from trader.indicator.OBV import OBV
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

def create_features(df, indicators=None, train=True):
    df_result = pd.DataFrame()
    # process MACD values
    macd = Indicator(MACD)
    if indicators:
        macd_indicator = indicators['MACD']
        macd.set_indicator(macd_indicator)
    macd.load_dataframe(df)
    df_result['MACD'] = np.array(macd.results())
    indicator_macd = macd.indicator

    # process OBV values
    obv = Indicator(OBV)
    obv.volume_key = 'quote_volume'
    if indicators:
        obv_indicator = indicators['OBV']
        obv.set_indicator(obv_indicator)
    obv.load_dataframe(df)
    df_result['OBV'] = np.array(obv.results())
    indicator_obv = obv.indicator

    # process RSI values
    rsi = Indicator(RSI, 14)
    rsi.close_key = 'close'
    if indicators:
        rsi_indicator = indicators['RSI']
        rsi.set_indicator(rsi_indicator)
    rsi.load_dataframe(df)
    rsi_result = np.array(rsi.results())
    rsi_result[rsi_result == 0] = np.nan
    df_result['RSI'] = rsi_result
    indicator_rsi = rsi.indicator

    if not indicators:
        indicators = {}
    indicators['MACD'] = indicator_macd
    indicators['OBV'] = indicator_obv
    indicators['RSI'] = indicator_rsi

    df_result = df_result.dropna()

    return df_result, indicators


def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df_train, indicators = create_features(df, train=True)
    print(df_train)

    scaler = MinMaxScaler(feature_range=(0, 1))
    #train_lsma_values = scaler.fit_transform(np.array(train_lsma_values).reshape(-1, 1))

    df_test = hkdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    y_act = df_test['close'].values
    #test_lsma_values = scaler.transform(np.array(test_lsma_values).reshape(-1, 1))

    # define generator
    n_features = 1
    n_input = 8
    #generator = TimeseriesGenerator(train_lsma_values, train_lsma_values, length=n_input, batch_size=32)
    # define model
    model = Sequential()
    model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    #model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)
    # make a one step prediction out of sample
    #x_input = mlhelper.series_to_supervised(test_lsma_values, n_input, 0).values
    #for i in range(0, len(x_input)):
    #    yhat = model.predict(x_input[i].reshape((1, n_input, n_features)), verbose=0)
    #    yhat = scaler.inverse_transform(yhat)
    #    y_pred.append(yhat[0][0])

    #y_act = y_act[n_input:len(y_pred)+n_input]
    #print(len(y_act))
    #print(len(y_pred))

    plt.subplot(211)
    #for i in crossups:
    #    plt.axvline(x=i, color='green')
    #for i in crossdowns:
    #    plt.axvline(x=i, color='red')
    fig1, = plt.plot(y_act, label=symbol)
    plt.legend(handles=[fig1])
    plt.subplot(212)
    #plt.legend(handles=[fig21, fig22])
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
