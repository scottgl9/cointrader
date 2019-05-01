# Hourly klines LSTM Machine Learning implementation

import os
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential, load_model, model_from_json
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.LSMA import LSMA
from trader.lib.Indicator import Indicator


class HourlyLSTM(object):
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

        self.weights_file = os.path.join(self.models_path, "{}_weights.h5".format(self.symbol))
        self.arch_file = os.path.join(self.models_path, "{}_arch.json".format(self.symbol))
        self.xscale_file = os.path.join(self.models_path, "{}_xscale.skl".format(self.symbol))
        self.yscale_file = os.path.join(self.models_path, "{}_yscale.skl".format(self.symbol))
        # hours to preload to initialize indicators
        self.columns = ['LSMA_CLOSE', 'RSI', 'OBV']
        self.batch_size=batch_size
        self.x_scaler = None
        self.y_scaler = None
        self.test_model = None
        self.model = None
        self.model_columns = 0
        self.model_rows = 0
        self.df = None
        self.lsma_close = None
        self.obv = None
        self.rsi = None
        self.start_ts = 0
        self.last_ts = 0
        self.model_end_ts = 0
        self.df_update = None
        self.testX = None
        self.scalers_loaded = False
        self.indicators_loaded = False
        self.test_result = 0
        self.predict_result = 0


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


    def create_scaler_model(self):
        df = self.hkdb.get_pandas_klines(self.symbol, start_ts=0, end_ts=self.model_end_ts)
        self.df = self.create_features(df)
        self.create_train_dataset(self.df, column='LSMA_CLOSE', transform=False)


    def load(self, start_ts=0, end_ts=0):
        self.model_end_ts = end_ts
        self.model = self.load_model()
        if self.model:
            # create test model from original model
            self.test_model = self.create_model(batch_size=1, model=self.model)
            return

        df = self.hkdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        # adjust size to take into account batch_size
        #adjusted_size = int(len(df) / self.batch_size) * self.batch_size + 1
        #df = df.iloc[:adjusted_size]

        self.start_ts = df['ts'].values.tolist()[-1]
        self.df = self.create_features(df)
        trainX, trainY = self.create_train_dataset(self.df, column='LSMA_CLOSE', transform=True)

        batch_adjusted_start  = len(trainX) - int(len(trainX) / self.batch_size) * self.batch_size
        trainX = trainX[batch_adjusted_start:]
        trainY = trainY[batch_adjusted_start:]

        # reshape for training
        trainX = np.reshape(trainX, (-1, len(self.columns), 1))

        self.model = self.train_model(trainX, trainY, epoch=20, batch_size=self.batch_size)
        self.indicators_loaded = True
        self.save_model(self.model)
        print("Saved {} model".format(self.symbol))
        # free up memory from self.df
        self.df = None
        # create test model from original model
        self.test_model = self.create_model(batch_size=1, model=self.model)


    def update(self, hourly_ts):
        if not self.scalers_loaded:
            self.create_scaler_model()
            self.indicators_loaded = True
            self.scalers_loaded = True

        # if we loaded the model from files, then self.indicators_loaded will be False
        # we need to run the indicators on a dataset to get them in a good state before
        # using the indicators to build features for test/predict
        if not self.indicators_loaded:
            self.init_indicators(start_ts=0, end_ts=self.model_end_ts)
            self.indicators_loaded = True

        df_update = self.hkdb.get_pandas_kline(self.symbol, hourly_ts=hourly_ts)
        #self.last_ts = df_update['ts'].values.tolist()[-1]
        self.df_update = self.create_features(df_update)
        if not len(self.df_update):
            return
        self.test_result = self.df_update['LSMA_CLOSE'].values[0]
        self.testX = self.create_test_dataset(self.df_update)
        predictY = self.test_model.predict(self.testX) #np.array( [self.testX,] ))
        predictY = self.y_scaler.inverse_transform(predictY)[0][0]
        self.predict_result = predictY
        #print("{} = {}".format(self.symbol, predictY))

    def create_train_dataset(self, dataset, column='close', transform=True):
        dataX = dataset.shift(1).dropna().values
        dataY = dataset[column].shift(-1).dropna().values

        dataY = dataY.reshape(-1, 1)

        self.x_scaler = MinMaxScaler(feature_range=(0, 1))
        self.y_scaler = MinMaxScaler(feature_range=(0, 1))

        if transform:
            scaleX = np.array(self.x_scaler.fit_transform(dataX))
            scaleY = np.array(self.y_scaler.fit_transform(dataY))
        else:
            self.x_scaler.fit(dataX)
            self.y_scaler.fit(dataY)
            scaleX = dataX
            scaleY = dataY

        self.model_columns = 3 #scaleX.shape[1]
        self.model_rows = 1 #scaleX.shape[2]

        return scaleX, scaleY

    def create_test_dataset(self, dataset):
        dataX = dataset.dropna().values
        scaleX = self.x_scaler.transform(dataX)
        testX = np.reshape(np.array(scaleX), (-1, len(self.columns), 1))
        return testX


    # initialize indicators if model loaded from file
    def init_indicators(self, start_ts, end_ts):
        df = self.hkdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        self.create_features(df, store=False)


    def create_features(self, df, store=True):
        # process LSMA close values
        lsma_close = Indicator(LSMA, 12)
        if self.lsma_close:
            lsma_close_indicator = self.lsma_close
            lsma_close.set_indicator(lsma_close_indicator)
        lsma_close.load_dataframe(df)
        if store:
            df['LSMA_CLOSE'] = np.array(lsma_close.results())
        else:
            lsma_close.process()

        if not self.lsma_close:
            self.lsma_close = lsma_close.indicator

        # process OBV values
        obv = Indicator(OBV, use_log10=True)
        #obv.close_key = 'LSMA_CLOSE'
        obv.volume_key = 'quote_volume'
        if self.obv:
            obv_indicator = self.obv
            obv.set_indicator(obv_indicator)
        obv.load_dataframe(df)
        if store:
            df['OBV'] = np.array(obv.results())
        else:
            obv.process()

        if not self.obv:
            self.obv = obv.indicator

        # process RSI values
        rsi = Indicator(RSI, 14)
        #rsi.close_key = 'LSMA_CLOSE'
        if self.rsi:
            rsi_indicator = self.rsi
            rsi.set_indicator(rsi_indicator)
        rsi.load_dataframe(df)
        if store:
            rsi_result = np.array(rsi.results())
            rsi_result[rsi_result == 0] = np.nan
            df['RSI'] = rsi_result
        else:
            rsi.process()
        if not self.rsi:
            self.rsi = rsi.indicator

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
        model = self.create_model(columns=X_train.shape[1], rows=X_train.shape[2], batch_size=batch_size)
        model.fit(X_train, Y_train, epochs=epoch, batch_size=batch_size)
        return model
