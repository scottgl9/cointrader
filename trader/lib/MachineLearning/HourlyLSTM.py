# Hourly klines LSTM Machine Learning implementation

import os
import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential, load_model, model_from_json
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
        if simulate_db_filename:
            name = os.path.basename(self.simulate_db_filename).replace('.db', '')
            self.models_path = os.path.join("models", name)
        else:
            self.models_path = os.path.join("models", "live")
        if not os.path.exists(self.models_path):
            os.mkdir(self.models_path)
        self.columns = ['LSMA_CLOSE', 'RSI', 'OBV']
        self.x_scaler = MinMaxScaler(feature_range=(0, 1))
        self.y_scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.df = None
        self.lsma_close = None
        self.obv = None
        self.rsi = None
        self.start_ts = 0
        self.last_ts = 0
        self.df_update = None
        self.testX = None

    def load_model(self):
        weights_file = os.path.join(self.models_path, "{}_weights.h5".format(self.symbol))
        if not os.path.exists(weights_file):
            return None
        arch_file = os.path.join(self.models_path, "{}_arch.json".format(self.symbol))
        if not os.path.exists(arch_file):
            return None
        with open(arch_file, 'r') as f:
            model = model_from_json(f.read())
        model.load_weights(weights_file)
        print("Loaded {} model".format(self.symbol))
        return model

    def save_model(self, model):
        weights_file = os.path.join(self.models_path, "{}_weights.h5".format(self.symbol))
        arch_file = os.path.join(self.models_path, "{}_arch.json".format(self.symbol))
        model.save_weights(weights_file)
        with open(arch_file, 'w') as f:
            f.write(model.to_json())

    def load(self, start_ts=0, end_ts=0):
        self.model = self.load_model()
        if self.model:
            return

        df = self.hkdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        self.start_ts = df['ts'].values.tolist()[-1]
        self.df = self.create_features(df)
        trainX, trainY = self.create_train_dataset(self.df, column='LSMA_CLOSE')

        # reshape for training
        trainX = np.reshape(trainX, (-1, len(self.columns), 1))

        self.model = self.train_model(trainX, trainY, epoch=20)
        self.save_model(self.model)
        print("Saved {} model".format(self.symbol))

    def update(self, start_ts, end_ts):
        df_update = self.hkdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        print(df_update)
        self.last_ts = df_update['ts'].values.tolist()[-1]
        self.df_update = self.create_features(df_update)
        self.testX = self.create_test_dataset(self.df_update)

    def create_train_dataset(self, dataset, column='close'):
        dataX = dataset.shift(1).dropna().values
        dataY = dataset[column].shift(-1).dropna().values

        dataY = dataY.reshape(-1, 1)

        scaleX = self.x_scaler.fit_transform(dataX)
        scaleY = self.y_scaler.fit_transform(dataY)
        return np.array(scaleX), np.array(scaleY)

    def create_test_dataset(self, dataset):
        dataX = dataset.values
        scaleX = self.x_scaler.fit_transform(dataX)
        testX = np.reshape(np.array(scaleX), (-1, len(self.columns), 1))
        return testX

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
        print(rsi_result)
        rsi_result[rsi_result == 0] = np.nan
        df['RSI'] = rsi_result

        df = pd.DataFrame(df, columns=self.columns)
        return df.dropna()

    def train_model(self, X_train, Y_train, epoch=25, batch_size=32):
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
        return model
