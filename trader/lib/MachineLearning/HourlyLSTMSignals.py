import os
import pandas as pd
import numpy as np
from trader.lib.DataFrameMLHelper import DataFrameMLHelper
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from numpy import hstack
from keras.preprocessing.sequence import TimeseriesGenerator
from trader.indicator.EMA import EMA
from trader.lib.Indicator import Indicator
from trader.lib.Crossover import Crossover


class HourlyLSTMSignals(object):
    def __init__(self, kdb, symbol, start_ts=0, simulate_db_filename=None, batch_size=32):
        self.kdb = kdb
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
        self.column_count = 3
        self.max_close = 0
        self.max_quote = 0
        self.batch_size = batch_size

        self.df_ml_helper = DataFrameMLHelper()

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
        self.ema_close1 = None
        self.ema_close2 = None
        self.volume_close = None
        self.indicators_loaded = False
        self.actual_result = 0
        self.predict_result = 0
        self.testX = None
        self.n_features = 0
        self.n_input = 0
        self.n_outputs = 0

    def load(self, model_start_ts=0, model_end_ts=0, test_start_ts=0, test_end_ts=0):
        self.model_start_ts = model_start_ts
        self.model_end_ts = model_end_ts
        self.test_start_ts = test_start_ts
        self.test_end_ts = test_end_ts

        self.max_quote = self.kdb.get_max_field_value(self.symbol, 'quote_volume', model_start_ts, model_end_ts)
        self.max_close = self.kdb.get_max_field_value(self.symbol, 'close', model_start_ts, model_end_ts)
        print("Max close={}".format(self.max_close))
        print("Max quote_volume={}".format(self.max_quote))

        self.df = self.kdb.get_pandas_klines(self.symbol, self.model_start_ts, self.model_end_ts)
        # normalize close and quote_volume to [0, 1]
        self.df['close'] /= self.max_close
        self.df['quote_volume'] /= self.max_quote

        self.start_ts = self.df['ts'].values.tolist()[-1]
        timestamps = self.df['ts']
        self.df = self.create_features(self.df)

        in_seq1 = self.df['EMA_CLOSE1'].values
        in_seq2 = self.df['EMA_CLOSE2'].values

        out_seq = self.generate_labels(in_seq1, in_seq2, timestamps)

        in_seq1 = in_seq1.reshape((len(in_seq1), 1))
        in_seq2 = in_seq2.reshape((len(in_seq2), 1))

        dataset = hstack((in_seq1, in_seq2))
        out_seq = out_seq.reshape((len(out_seq), 1))
        self.n_features = dataset.shape[1]
        self.n_input = self.column_count
        self.n_outputs = 1

        generator = TimeseriesGenerator(dataset, out_seq, length=self.n_input, batch_size=8)
        # for i in range(len(generator)):
        #     x, y = generator[i]
        #     print('%s => %s' % (x, y))
        #     if i == 100:
        #         break
        self.model = self.create_model(self.n_input, self.n_features, self.n_outputs)
        self.model.fit_generator(generator, steps_per_epoch=1, epochs=500, verbose=1)
        #model.fit(dataset, out_seq, epochs=500, batch_size=8, verbose=True)

        self.indicators_loaded = True
        # free up memory from self.df
        self.df = None
        # create test model from original model
        #self.test_model = self.create_model(n_input, n_features, n_outputs)

    def update(self, hourly_ts):
        # if we loaded the model from files, then self.indicators_loaded will be False
        # we need to run the indicators on a dataset to get them in a good state before
        # using the indicators to build features for test/predict
        if not self.indicators_loaded:
            self.init_indicators(start_ts=0, end_ts=self.model_end_ts)
            self.indicators_loaded = True

        hourly_end_ts = hourly_ts
        hourly_start_ts = hourly_ts - 1000 * 3600 * (self.column_count - 1)
        df_update = self.kdb.get_pandas_klines(self.symbol, hourly_start_ts, hourly_end_ts)
        #df_update = self.kdb.get_pandas_kline(self.symbol, hourly_ts=hourly_ts)

        # normalize close and quote_volume to [0, 1]
        df_update['close'] /= self.max_close
        df_update['quote_volume'] /= self.max_quote

        #self.last_ts = df_update['ts'].values.tolist()[-1]
        self.df_update = self.create_features(df_update, store=True)
        if not len(self.df_update):
            return
        values1 = self.df_update['EMA_CLOSE1'].values
        values2 = self.df_update['EMA_CLOSE2'].values
        if len(values1) != self.column_count or len(values2) != self.column_count:
            return
        self.testX = np.array([values1, values2]).reshape((1, self.n_input, self.n_features))
        predictY = self.model.predict(self.testX)
        if predictY:
            self.predict_result = predictY[0][0]
            if self.predict_result < 0.4 or self.predict_result > 0.6:
                print(self.predict_result)

    def create_model(self, n_input, n_features, n_outputs):
        new_model = Sequential()

        new_model.add(LSTM(units=50, return_sequences=True, input_shape=(n_input, n_features)))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50, return_sequences=True))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50, return_sequences=True))
        new_model.add(Dropout(0.2))

        new_model.add(LSTM(units=50))
        new_model.add(Dropout(0.2))

        new_model.add(Dense(units=1))

        new_model.compile(optimizer='adam', loss='mean_squared_error')
        return new_model

    def generate_labels(self, in_seq1, in_seq2, timestamps):
        out_seq = []
        in_size = len(in_seq1)
        cross = Crossover(window=5)
        for i in range(0, in_size):
            cross.update(in_seq1[i], in_seq2[i])#, ts=timestamps[i])
            if cross.crossup_detected():
                print("CROSSUP")
                out_seq.append(0.9)
            elif cross.crossdown_detected():
                print("CROSSDOWN")
                out_seq.append(0.1)
            else:
                out_seq.append(0.5)
        return np.array(out_seq)

    # initialize indicators if model loaded from file
    def init_indicators(self, start_ts, end_ts):
        df = self.kdb.get_pandas_klines(self.symbol, start_ts, end_ts)
        df['close'] /= self.max_close
        df['quote_volume'] /= self.max_quote
        self.create_features(df, store=False)

    def create_features(self, df, store=True):
        # process EMA close values
        ema_close = Indicator(EMA, 12, scale=1)
        if self.ema_close1:
            ema_close_indicator = self.ema_close1
            ema_close.set_indicator(ema_close_indicator)
        ema_close.load_dataframe(df)
        if store:
            df['EMA_CLOSE1'] = np.array(ema_close.results())
        else:
            ema_close.process()

        self.ema_close1 = ema_close.indicator

        ema_close2 = Indicator(EMA, 50, scale=1)
        if self.ema_close2:
            ema_close_indicator2 = self.ema_close2
            ema_close2.set_indicator(ema_close_indicator2)
        ema_close2.load_dataframe(df)
        if store:
            df['EMA_CLOSE2'] = np.array(ema_close2.results())
        else:
            ema_close2.process()

        self.ema_close2 = ema_close2.indicator

        if store:
            df = pd.DataFrame(df, columns=['EMA_CLOSE1', 'EMA_CLOSE2'])
            return df.dropna()
        return None
