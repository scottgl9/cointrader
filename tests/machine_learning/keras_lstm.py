#!/usr/bin/env python3
# https://github.com/dashee87/blogScripts/blob/master/Jupyter/2017-11-20-predicting-cryptocurrency-prices-with-deep-learning.ipynb
# import the relevant Keras modules
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.layers import LSTM
from keras.layers import Dropout
import numpy as np
import pandas as pd
import talib

class MTS_LSTM(object):
    def __init__(self, win_secs=3600, update_win_secs=900):
        self.win_secs = win_secs
        self.update_win_secs = update_win_secs
        self.start_ts = 0
        self.secs = []
        self.closes = []
        self.lows = []
        self.highs = []
        self.base_volumes = []
        self.quote_volumes = []
        self.model = None
        self.full = False
        self.init_model = True

    def update(self, close, low, high, base_volume, quote_volume, ts):
        if not self.start_ts:
            self.start_ts = ts
        sec = (ts - self.start_ts) / 1000.0

        self.secs.append(sec)
        self.closes.append([close])
        self.lows.append([low])
        self.highs.append([high])
        self.base_volumes.append([base_volume])
        self.quote_volumes.append([quote_volume])

        cnt = 0
        while (sec - self.secs[cnt]) > self.win_secs:
            cnt += 1

        if cnt != 0:
            self.secs = self.secs[cnt:]
            self.closes = self.closes[cnt:]
            self.lows = self.lows[cnt:]
            self.highs = self.highs[cnt:]
            self.base_volumes = self.base_volumes[cnt:]
            self.quote_volumes = self.quote_volumes[cnt:]
            if not self.full:
                self.full = True

        if not self.full:
            return

        if self.init_model:
            # build initial model
            inputs = np.array([np.array(self.closes), np.array(self.lows), np.array(self.highs)])
            self.build_init_model(inputs)
            self.init_model = False
            return

    def build_init_model(self, inputs, output_size=1, neurons=20, activ_func="linear",
                dropout=0.25, loss="mae", optimizer="adam"):
        self.model = Sequential()

        self.model.add(LSTM(neurons, input_shape=(inputs.shape[1], inputs.shape[2])))
        self.model.add(Dropout(dropout))
        self.model.add(Dense(units=output_size))
        self.model.add(Activation(activ_func))
        self.model.compile(loss=loss, optimizer=optimizer)
        self.model.save("models/ETHBTC.h5")

    def update_model(self, inputs):
        #self.model.fit()
        pass


if __name__ == '__main__':
    np.random.seed(202)
    mts_lstm = MTS_LSTM()
    dataset = pd.read_csv('ETHBTC_klines.csv')
    dataset = dataset.dropna()
    #dataset = dataset[['Open', 'High', 'Low', 'Close', 'base_volume', 'quote_volume']]
    timestamps = dataset['timestamp'].values
    open_prices = dataset['Open'].values
    close_prices = dataset['Close'].values
    high_prices = dataset['High'].values
    low_prices = dataset['Low'].values
    base_volumes = dataset['base_volume'].values
    quote_volumes = dataset['quote_volume'].values

    for i in range(0, len(close_prices)):
        mts_lstm.update(close=close_prices[i],
                        low=low_prices[i],
                        high=high_prices[i],
                        base_volume=base_volumes[i],
                        quote_volume=quote_volumes[i],
                        ts=timestamps[i])
