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
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.binance.AccountBinance import AccountBinance
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from trader.lib.Indicator import Indicator
from trader.indicator.ADL import ADL
from trader.indicator.EMA import EMA
from trader.indicator.KST import KST
from trader.indicator.MACD import MACD
from trader.indicator.OBV import OBV
from trader.indicator.ROC import ROC
from trader.indicator.RSI import RSI
from trader.indicator.TSI import TSI

from numpy import hstack
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from sklearn.preprocessing import MinMaxScaler


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
    roc = Indicator(ROC, window=1, smoother=EMA(12)) #, scale=12)
    roc.close_key = "CLOSE"
    try:
        roc_indicator = indicators['ROC']
        roc.set_indicator(roc_indicator)
    except KeyError:
        pass
    roc.load_dataframe(df)
    df_result['ROC'] = np.array(roc.results())
    indicator_roc = roc.indicator
    indicators['ROC'] = indicator_roc
    return df_result, indicators


def create_features(df, indicators=None):
    df_result = pd.DataFrame()

    # process MACD values
    macd = Indicator(MACD) #, scale=12)
    macd.close_key = "close"
    try:
        macd_indicator = indicators['MACD']
        macd.set_indicator(macd_indicator)
    except KeyError:
        pass
    macd.load_dataframe(df)
    df_result['MACD'] = np.array(macd.results())
    df_result['MACDHIST'] = np.array(macd.results()) - np.array(macd.results(1))
    indicator_macd = macd.indicator

    # process OBV values
    obv = Indicator(OBV, use_log10=True)
    obv.close_key = 'close'
    obv.volume_key = 'quote_volume'
    try:
        obv_indicator = indicators['OBV']
        obv.set_indicator(obv_indicator)
    except KeyError:
        pass
    obv.load_dataframe(df)
    df_result['OBV'] = np.array(obv.results())
    indicator_obv = obv.indicator
    #df_result['VOLUME'] = df['quote_volume']

    # process RSI values
    rsi = Indicator(RSI, 14) #, smoother=EMA(1, scale=24))
    rsi.close_key = 'close'
    try:
        rsi_indicator = indicators['RSI']
        rsi.set_indicator(rsi_indicator)
    except KeyError:
        pass
    rsi.load_dataframe(df)
    rsi_result = np.array(rsi.results())
    rsi_result[rsi_result == 0] = np.nan
    #df_result['RSI'] = rsi_result
    indicator_rsi = rsi.indicator

    # process adl values
    adl = Indicator(ADL)
    adl.close_key = 'close'
    adl.volume_key = 'quote_volume'
    try:
        adl_indicator = indicators['ADL']
        adl.set_indicator(adl_indicator)
    except KeyError:
        pass
    adl.load_dataframe(df)
    adl_result = np.array(adl.results())
    #df_result['ADL'] = adl_result
    indicator_adl = adl.indicator

    # process ATR values
    # atr = Indicator(ATR, 14)
    # try:
    #     atr_indicator = indicators['ATR']
    #     atr.set_indicator(atr_indicator)
    # except KeyError:
    #     pass
    # atr.load_dataframe(df)
    # atr_result = np.array(atr.results())
    # #rsi_result[rsi_result == 0] = np.nan
    # df_result['ATR'] = atr_result
    # indicator_atr = atr.indicator

    # process PPO values
    # ppo = Indicator(PPO)
    # try:
    #     ppo_indicator = indicators['PPO']
    #     ppo.set_indicator(ppo_indicator)
    # except KeyError:
    #     pass
    # ppo.load_dataframe(df)
    # ppo_result = np.array(ppo.results())
    # df_result['PPO'] = ppo_result
    # indicator_ppo = ppo.indicator

    # process EFI values
    # efi = Indicator(EFI, 13, scale=24)
    # efi.close_key = 'CLOSE'
    # efi.volume_key = 'quote_volume'
    # try:
    #     efi_indicator = indicators['EFI']
    #     efi.set_indicator(efi_indicator)
    #     except KeyError:
    #         pass
    # efi.load_dataframe(df)
    # efi_result = np.array(efi.results())
    # df_result['EFI'] = efi_result
    # indicator_efi = efi.indicator

    # process KST values
    kst = Indicator(KST)
    kst.close_key = 'close'
    try:
        kst_indicator = indicators['KST']
        kst.set_indicator(kst_indicator)
    except KeyError:
        pass
    kst.load_dataframe(df)
    kst_result = np.array(kst.results())
    #df_result['KST'] = kst_result
    indicator_kst = kst.indicator

    # process TSI values
    tsi = Indicator(TSI)
    tsi.close_key = 'close'
    try:
        tsi_indicator = indicators['TSI']
        tsi.set_indicator(tsi_indicator)
    except KeyError:
        pass
    tsi.load_dataframe(df)
    tsi_result = np.array(tsi.results())
    #df_result['TSI'] = tsi_result
    indicator_tsi = tsi.indicator

    if not indicators:
        indicators = {}
    indicators['MACD'] = indicator_macd
    indicators['OBV'] = indicator_obv
    indicators['RSI'] = indicator_rsi
    indicators['ADL'] = indicator_adl
    indicators['TSI'] = indicator_tsi
    indicators['KST'] = indicator_kst
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

def simulate(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    mlhelper = DataFrameMLHelper()
    df = kdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df, indicators = process_raw_klines(df)
    df_train, indicators = create_features(df, indicators)
    #df_train = df_train.drop(columns="CLOSE")
    df_labels, indicators = create_labels(df, indicators)
    train_label_values = df_labels['ROC'].values[:df_train.count().iloc[0]]
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
        df2 = kdb.get_pandas_klines(symbol, start_ts, end_ts)
        df2, indicators = process_raw_klines(df2, indicators)
        test_df, indicators = create_features(df2, indicators)
        test_labels_df, indicators = create_labels(df2, indicators)
        if test_labels_df['ROC'].size:
            y_act.append(test_labels_df['ROC'].values[-1])
        if df2['CLOSE'].size:
            prices.append(df2['CLOSE'].values[-1])
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
