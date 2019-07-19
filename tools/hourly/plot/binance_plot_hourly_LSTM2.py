#!/usr/bin/python
# new version of HourlyLSTM

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
from trader.account.binance.client import Client
from trader.config import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential, load_model, model_from_json
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.LSMA import LSMA
from trader.indicator.EMA import EMA
from trader.lib.Indicator import Indicator

try:
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.EMA import EMA


class HourlyLSTM2(object):
    def __init__(self, hkdb, symbol, start_ts=0, simulate_db_filename=None, batch_size=32):
        self.hkdb = hkdb
        self.symbol = symbol
        self.start_ts = start_ts
        self.simulate_db_filename = simulate_db_filename
        if simulate_db_filename:
            name = os.path.basename(self.simulate_db_filename).replace('.db', '')
            self.models_path = os.path.join("models", name)
        else:
            self.models_path = os.path.join("models", "live")
        if not os.path.exists(self.models_path):
            os.mkdir(self.models_path)
        self.columns = ['close', 'quote_volume', 'EMA_CLOSE']
        self.max_close = 0
        self.max_quote = 0

        self.weights_file = os.path.join(self.models_path, "{}_weights.h5".format(self.symbol))
        self.arch_file = os.path.join(self.models_path, "{}_arch.json".format(self.symbol))
        self.start_ts = 0
        self.last_ts = 0
        self.model_start_ts = 0
        self.model_end_ts = 0
        self.test_start_ts = 0
        self.test_end_ts = 0
        self.df = None
        self.model = None
        self.test_model = None
        self.ema_close = None
        self.volume_close = None

    def load_model(self):
        if not os.path.exists(self.weights_file):
            return None
        if not os.path.exists(self.arch_file):
            return None
        with open(self.arch_file, 'r') as f:
            model = model_from_json(f.read())
        model.load_weights(self.weights_file)
        print("Loaded {} model".format(self.symbol))
        return model

    def save_model(self, model):
        model.save_weights(self.weights_file)
        with open(self.arch_file, 'w') as f:
            f.write(model.to_json())

    def load(self, model_start_ts=0, model_end_ts=0, test_start_ts=0, test_end_ts=0):
        self.model_start_ts = model_start_ts
        self.model_end_ts = model_end_ts
        self.test_start_ts = test_start_ts
        self.test_end_ts = test_end_ts

        self.model = self.load_model()
        if self.model:
            # create test model from original model
            self.test_model = self.create_model(batch_size=1, model=self.model)
            return
        self.max_quote = hkdb.get_max_field_value(symbol, 'quote_volume', model_start_ts, model_end_ts)
        self.max_close = hkdb.get_max_field_value(symbol, 'close', model_start_ts, model_end_ts)
        print("Max close={}".format(self.max_close))
        print("Max quote_volume={}".format(self.max_quote))

        self.df = self.hkdb.get_pandas_klines(self.symbol, self.model_start_ts, self.model_end_ts)
        # normalize close and quote_volume to [0, 1]
        self.df['close'] /= self.max_close
        self.df['quote_volume'] /= self.max_quote

        self.start_ts = self.df['ts'].values.tolist()[-1]
        #self.df = self.create_features(self.df)

    def create_features(self, df, store=True):
        # process EMA close values
        ema_close = Indicator(EMA, 12, scale=24)
        if self.ema_close:
            ema_close_indicator = self.ema_close
            ema_close.set_indicator(ema_close_indicator)
        ema_close.load_dataframe(df)
        if store:
            df['EMA_CLOSE'] = np.array(ema_close.results())
        else:
            ema_close.process()

        self.ema_close = ema_close.indicator

        if store:
            df = pd.DataFrame(df, columns=self.columns)
            return df.dropna()
        return None

    def create_model(self, columns=3, rows=1, batch_size=32, model=None):
        new_model = Sequential()

        new_model.add(LSTM(units=50, return_sequences=True, batch_input_shape=(batch_size, columns, rows)))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50, return_sequences=True))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50, return_sequences=True))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50))
        new_model.add(Dropout(0.2))

        new_model.add(Dense(units=1))

        # for reshaping batch_size from a previously created model
        if model:
            weights = model.get_weights()
            new_model.set_weights(weights)

        new_model.compile(optimizer='adam', loss='mean_squared_error')
        return new_model

    def train_model(self, X_train, Y_train, epoch=25, batch_size=32):
        model = self.create_model(columns=len(self.columns), rows=X_train.shape[2], batch_size=batch_size)
        model.fit(X_train, Y_train, epochs=epoch, batch_size=batch_size)
        return model


def simulate(hkdb, symbol, start_ts, end_ts):
    hourly_lstm = HourlyLSTM2(hkdb, symbol)

    hourly_lstm.load(model_start_ts=0, model_end_ts=start_ts)

    testy = []
    predicty = []

    count = 0

    ts = start_ts
    #while ts <= end_ts:
    #    ts += 3600 * 1000
    #    hourly_lstm.update(ts)
    #    testy.append(hourly_lstm.actual_result)
    #    predicty.append(hourly_lstm.predict_result)
    #    count += 1

    plt.subplot(211)
    #fig1, = plt.plot(testy, label='TESTY')
    #fig2, = plt.plot(predicty, label='PREDICTY')
    fig1, = plt.plot(hourly_lstm.df['close'].values.tolist(), label='close')
    #fig2, = plt.plot(hourly_lstm.df['EMA_CLOSE'].values.tolist(), label='EMA')
    plt.legend(handles=[fig1])
    plt.subplot(212)
    fig21, = plt.plot(hourly_lstm.df['quote_volume'].values.tolist(), label='volume')
    plt.legend(handles=[fig21])
    plt.show()

# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

def get_last_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #c.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E DESC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

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

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)


    hkdb = HourlyKlinesDB(accnt, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        timestamps = hkdb.get_kline_values_by_column(symbol, 'ts')
        train_index = int(len(timestamps) * 0.80)
        start_ts = int(timestamps[train_index])
        end_ts = int(timestamps[-1])
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()
