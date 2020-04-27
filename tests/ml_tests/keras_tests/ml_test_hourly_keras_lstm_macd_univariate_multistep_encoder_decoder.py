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
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD

from keras.models import Sequential, model_from_json
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import TimeDistributed, RepeatVector
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


# split a univariate sequence into samples
def split_sequence(sequence, n_steps_in, n_steps_out):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out
        # check if we are beyond the sequence
        if out_end_ix > len(sequence):
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:out_end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


def simulate(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    models_path = "models"
    weights_file = os.path.join(models_path, "{}_weights.h5".format(symbol))
    arch_file = os.path.join(models_path, "{}_arch.json".format(symbol))
    mlhelper = DataFrameMLHelper()
    scaler = MinMaxScaler(feature_range=(0, 1))

    df = kdb.get_pandas_klines(symbol, train_start_ts, train_end_ts)
    df, indicators = process_raw_klines(df)
    df_train, indicators = create_features(df, indicators)

    n_features = 1
    n_steps_in, n_steps_out = 3, 3

    macd_values = df_train['MACD'].values
    scaled_macd_values = scaler.fit_transform(macd_values.reshape(-1, 1))

    X, Y = split_sequence(scaled_macd_values, n_steps_in, n_steps_out)

    trainX = X.reshape((X.shape[0], X.shape[1], n_features))
    trainy = Y.reshape((Y.shape[0], Y.shape[1], n_features))

    if os.path.exists(weights_file) and os.path.exists(arch_file):
        with open(arch_file, 'r') as f:
            model = model_from_json(f.read())
        model.load_weights(weights_file)
        print("Loaded {} model".format(symbol))
    else:
        model = Sequential()
        model.add(LSTM(100, activation='relu', input_shape=(n_steps_in, n_features)))
        model.add(RepeatVector(n_steps_out))
        model.add(LSTM(100, activation='relu', return_sequences=True))
        model.add(TimeDistributed(Dense(1)))
        model.compile(optimizer='adam', loss='mse')
        # fit model
        #model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)
        model.fit(trainX, trainy, epochs=5, verbose=1, batch_size=8, shuffle=True)
        model.save_weights(weights_file)
        with open(arch_file, 'w') as f:
            f.write(model.to_json())

    y_act = []
    y_act2 = []
    y_pred = []
    y_pred2 = []
    prices = []
    ts = test_start_ts
    while ts <= test_end_ts:
        start_ts = ts
        end_ts = ts + 1000 * 3600 * (n_steps_in - 1)
        df2 = kdb.get_pandas_klines(symbol, start_ts, end_ts)
        df2, indicators = process_raw_klines(df2, indicators)
        test_df, indicators = create_features(df2, indicators)
        if test_df['MACD'].size:
            y_act.append(test_df['MACD'].values[-1])
        #if test_labels_df['MHIST'].size:
        #    y_act2.append(test_labels_df['MHIST'].values[-1])
        if df2['CLOSE'].size:
            prices.append(df2['CLOSE'].values[-1])
       # test_df = test_df.drop(columns="CLOSE")
        try:
            test_dataset = np.array([scaler.transform(test_df.values)])
            #print(test_dataset)
            prediction = model.predict(test_dataset)
            #prediction2 = model.predict(prediction)
            #print(prediction2)
            prediction = scaler.inverse_transform(prediction[0])
            y_pred.append(prediction[2][0])
            #y_pred2.append(prediction[1][0])
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
    #fig23, = plt.plot(y_pred2, label='pred2')
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


    #config = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 8})
    #sess = tf.Session(config=config)
    #keras.backend.set_session(sess)

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
