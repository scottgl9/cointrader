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
from trader.indicator.ATR import ATR
from trader.indicator.PPO import PPO
from trader.indicator.EFI import EFI
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
    # process LSMA close values
    lsma_close = Indicator(LSMA, 26)
    if indicators:
        lsma_close_indicator = indicators['LSMA']
        lsma_close.set_indicator(lsma_close_indicator)
    lsma_close.load_dataframe(df)
    df_result['LSMA_CLOSE'] = np.array(lsma_close.results())
    df['LSMA_CLOSE'] = df_result['LSMA_CLOSE']
    indicator_lsma = lsma_close.indicator

    # process MACD values
    macd = Indicator(MACD) #, scale=12)
    macd.close_key = "LSMA_CLOSE"
    if indicators:
        macd_indicator = indicators['MACD']
        macd.set_indicator(macd_indicator)
    macd.load_dataframe(df)
    #df_result['MACD'] = np.array(macd.results())
    df_result['MACDHIST'] = np.array(macd.results()) - np.array(macd.results(1))
    indicator_macd = macd.indicator

    # process OBV values
    obv = Indicator(OBV)
    obv.close_key = 'LSMA_CLOSE'
    obv.volume_key = 'quote_volume'
    if indicators:
        obv_indicator = indicators['OBV']
        obv.set_indicator(obv_indicator)
    obv.load_dataframe(df)
    df_result['OBV'] = np.array(obv.results())
    indicator_obv = obv.indicator
    #df_result['VOLUME'] = df['quote_volume']

    # process RSI values
    rsi = Indicator(RSI, 14) #, smoother=EMA(12, scale=12))
    rsi.close_key = 'LSMA_CLOSE'
    if indicators:
        rsi_indicator = indicators['RSI']
        rsi.set_indicator(rsi_indicator)
    rsi.load_dataframe(df)
    rsi_result = np.array(rsi.results())
    rsi_result[rsi_result == 0] = np.nan
    df_result['RSI'] = rsi_result
    indicator_rsi = rsi.indicator

    # process ATR values
    # atr = Indicator(ATR, 14)
    # if indicators:
    #     atr_indicator = indicators['ATR']
    #     atr.set_indicator(atr_indicator)
    # atr.load_dataframe(df)
    # atr_result = np.array(atr.results())
    # #rsi_result[rsi_result == 0] = np.nan
    # df_result['ATR'] = atr_result
    # indicator_atr = atr.indicator

    # process PPO values
    # ppo = Indicator(PPO)
    # if indicators:
    #     ppo_indicator = indicators['PPO']
    #     ppo.set_indicator(ppo_indicator)
    # ppo.load_dataframe(df)
    # ppo_result = np.array(ppo.results())
    # df_result['PPO'] = ppo_result
    # indicator_ppo = ppo.indicator

    # process PPO values
    # efi = Indicator(EFI)
    # efi.volume_key = 'quote_volume'
    # if indicators:
    #     efi_indicator = indicators['EFI']
    #     efi.set_indicator(efi_indicator)
    # efi.load_dataframe(df)
    # efi_result = np.array(efi.results())
    # df_result['EFI'] = efi_result
    # indicator_efi = efi.indicator

    if not indicators:
        indicators = {}
    indicators['LSMA'] = indicator_lsma
    indicators['MACD'] = indicator_macd
    indicators['OBV'] = indicator_obv
    indicators['RSI'] = indicator_rsi
    #indicators['PPO'] = indicator_ppo
    #indicators['EFI'] = indicator_efi

    #indicators['ATR'] = indicator_atr

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

def transform_multi_feature_to_lagged(n_features, n_input):
    pass

def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    df = hkdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df_train, indicators = create_features(df, train=True)
    df_train = df_train.drop(columns="LSMA_CLOSE")
    train_close_values = df['close'].values[:df_train.count().iloc[0]]
    dataset = df_train.values
    xscaler = MinMaxScaler(feature_range=(0, 1))
    yscaler = MinMaxScaler(feature_range=(0, 1))
    trainX = xscaler.fit_transform(dataset)
    #print(trainX)
    trainY = yscaler.fit_transform(train_close_values.reshape(-1, 1))
    #print(trainX)
    #print(train_close_values)

    y_act = [] #hkdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)['close'].values

    #test_lsma_values = scaler.transform(np.array(test_lsma_values).reshape(-1, 1))

    # define generator
    n_features = trainX.shape[1]
    n_input = 8
    generator = TimeseriesGenerator(trainX, trainY, length=n_input, batch_size=n_input)
    last_generated, _ = generator[len(generator) - 1]
    #print(last_generated[0][-1])
    #for i in range(len(generator)):
    #    x, y = generator[i]
    #    print('{}'.format(x))

    model = Sequential()
    model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)

    y_pred = []
    ts = test_start_ts
    while ts <= test_end_ts:
        start_ts = ts
        end_ts = ts + 1000 * 3600 * (n_input - 1)
        df2 = hkdb.get_pandas_klines(symbol, start_ts, end_ts)
        test_df, indicators = create_features(df2, indicators)
        if test_df['LSMA_CLOSE'].size:
            y_act.append(test_df['LSMA_CLOSE'].values[-1])
        test_df = test_df.drop(columns="LSMA_CLOSE")
        try:
            test_dataset = np.array([xscaler.transform(test_df.values)])
            prediction = yscaler.inverse_transform(model.predict(test_dataset))
            y_pred.append(prediction[0][0])
        except ValueError:
            pass
        ts += 1000 * 3600
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
    fig2, = plt.plot(y_pred, label='pred')
    plt.legend(handles=[fig1, fig2])
    plt.subplot(212)
    #plt.legend(handles=[fig21, fig22])
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
