# Hourly klines LSTM Machine Learning implementation

import os
import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.LSMA import LSMA
from trader.lib.Indicator import Indicator

class HourlyLSTM(object):
    def __init__(self, hkdb, symbol, start_ts=0, simulate_db_filename=None):
        self.hkdb = hkdb
        self.symbol = symbol
        self.start_ts = start_ts
        self.simulate_db_filename = simulate_db_filename
        self.columns = ['LSMA_CLOSE', 'RSI', 'OBV']
        self.x_scaler = MinMaxScaler(feature_range=(0, 1))
        self.y_scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.df = None
        self.lsma_close = None
        self.obv = None
        self.rsi = None

    def load(self, start_ts=0, end_ts=0):
        df = self.hkdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        trainX, trainY = self.create_features(df)
        self.model = self.train_model(trainX, trainY, epoch=15)

    def create_dataset(self, dataset, column='close'):
        dataX = dataset.shift(1).dropna().values
        dataY = dataset[column].shift(-1).dropna().values

        dataY = dataY.reshape(-1, 1)

        scaleX = self.x_scaler.fit_transform(dataX)
        scaleY = self.y_scaler.fit_transform(dataY)
        return np.array(scaleX), np.array(scaleY)

    def create_features(self, df):
        # process LSMA close values
        self.lsma_close = Indicator(LSMA, 12)
        self.lsma_close.load_dataframe(df)
        df['LSMA_CLOSE'] = np.array(self.lsma_close.results())

        # process OBV values
        self.obv = Indicator(OBV)
        self.obv.volume_key = 'quote_volume'
        self.obv.load_dataframe(df)
        df['OBV'] = np.array(self.obv.results())

        # process RSI values
        self.rsi = Indicator(RSI, 14)
        self.rsi.close_key = 'LSMA_CLOSE'
        self.rsi.load_dataframe(df)
        rsi_result = np.array(self.rsi.results())
        rsi_result[rsi_result == 0] = np.nan
        df['RSI'] = rsi_result

        df = pd.DataFrame(df, columns=self.columns)
        self.df = df.dropna()
        X, Y = self.create_dataset(self.df, column='LSMA_CLOSE')

        # reshape for training
        X = np.reshape(X, (-1, len(self.columns), 1))
        return X, Y

    def train_model(self, X_train, Y_train, epoch=50, batch_size=32):
        filename = "models/{}.h5".format(self.symbol)
        if os.path.exists(filename):
            model = load_model(filename)
            return model

        model = Sequential()

        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(Dropout(0.2))

        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(units=50))
        model.add(Dropout(0.2))

        model.add(Dense(units=1))

        model.compile(optimizer='adam', loss='mean_squared_error')

        model.fit(X_train, Y_train, epochs=epoch, batch_size=batch_size)
        model.save(filename)
        return model
