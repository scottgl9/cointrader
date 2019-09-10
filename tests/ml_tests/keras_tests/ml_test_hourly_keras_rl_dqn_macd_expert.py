#!/usr/bin/env python3
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
import math
import logging
import time
from trader.account.binance.client import Client
from trader.config import *
import matplotlib.pyplot as plt
import argparse
from trader.lib.MachineLearning.HourlyLSTM import HourlyLSTM
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.account.AccountBinance import AccountBinance
import keras
import tensorflow as tf
from tensorflow.python.client import device_lib
from sklearn.preprocessing import MinMaxScaler
import random
from collections import deque
import numpy as np
import keras.backend as K
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Activation, Dense
from keras.optimizers import RMSprop
from keras.initializers import VarianceScaling
from trader.signal.hourly.Hourly_MACD_Signal import Hourly_MACD_Signal

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def huber_loss(y_true, y_pred, clip_delta=1.0):
    """ Huber loss - Custom Loss Function for Q Learning

    Links: 	https://en.wikipedia.org/wiki/Huber_loss
                    https://jaromiru.com/2017/05/27/on-using-huber-loss-in-deep-q-learning/
    """
    error = y_true - y_pred
    cond = K.abs(error) <= clip_delta
    squared_loss = 0.5 * K.square(error)
    quadratic_loss = 0.5 * K.square(clip_delta) + clip_delta * (K.abs(error) - clip_delta)
    return K.mean(tf.where(cond, squared_loss, quadratic_loss))


class DQNAgent:
    """ Stock Trading Bot """

    def __init__(self, state_size, pretrained=False, model_name=None, max_inventory=1):
        '''agent config'''
        self.state_size = state_size    	# normalized previous days
        self.action_size = 3           		# [sit, buy, sell]
        self.model_name = model_name
        self.max_inventory = max_inventory
        self.inventory = []
        self.memory = deque(maxlen=1000)
        self.first_iter = True
        self.episode = 0

        '''model config'''
        self.model_name = model_name
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.loss = huber_loss
        self.custom_objects = {'huber_loss': huber_loss}  # important for loading the model from memory
        self.optimizer = RMSprop(lr=self.learning_rate)
        self.initializer = VarianceScaling()

        '''load pretrained model'''
        if pretrained and self.model_name is not None:
            self.model = self.load()
        else:
            self.model = self._model()

    def _model(self):
        """	Creates the model. """
        model = Sequential()
        model.add(Dense(units=24, input_dim=self.state_size, kernel_initializer=self.initializer))
        model.add(Activation('relu'))
        model.add(Dense(units=64, kernel_initializer=self.initializer))
        model.add(Activation('relu'))
        model.add(Dense(units=64, kernel_initializer=self.initializer))
        model.add(Activation('relu'))
        model.add(Dense(units=24, kernel_initializer=self.initializer))
        model.add(Activation('relu'))
        model.add(Dense(units=self.action_size, kernel_initializer=self.initializer))

        model.compile(loss=self.loss, optimizer=self.optimizer)
        return model

    def remember(self, state, action, reward, next_state, done):
        """ Adds relevant data to memory. """
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, is_eval=False):
        """ Take action from given possible set of actions. """
        if not is_eval and random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        if self.first_iter:
            self.first_iter = False
            return 1
        options = self.model.predict(state)
        return np.argmax(options[0])

    def train_experience_replay(self, batch_size):
        """ Train on previous experiences in memory. """
        mini_batch = random.sample(self.memory, batch_size)

        X_train, y_train = [], []

        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target
            X_train.append(state[0])
            y_train.append(target_f[0])

        history = self.model.fit(np.array(X_train), np.array(y_train), epochs=1, verbose=0)
        loss = history.history['loss'][0]

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return loss

    def save(self, episode):
        self.model.save('models/{}_{}'.format(self.model_name, episode))

    def load(self):
        return load_model('models/' + self.model_name, custom_objects=self.custom_objects)

# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


def sigmoid(x):
    """ Computes sigmoid activation.

    Args:
            x (float): input value to sigmoid function.
    Returns:
            float: sigmoid function output.
    """
    try:
        if x < 0:
            return 1 - 1 / (1 + math.exp(x))
        return 1 / (1 + math.exp(-x))
    except OverflowError as err:
        print("Overflow err: {0} - Val of x: {1}".format(err, x))
    except ZeroDivisionError:
        print("division by zero!")
    except Exception as err:
        print("Error in sigmoid: " + err)

def getState(data, t, n_days):
    """ Returns an n-day state representation ending at time t. """
    d = t - n_days + 1
    block = data[d: t + 1] if d >= 0 else -d * [data[0]] + data[0: t + 1]  # pad with t0
    res = []
    for i in range(n_days - 1):
        res.append(sigmoid(block[i + 1] - block[i]))
    return np.array([res])


def run_expert_signal(hkdb, symbol, start_ts, end_ts):
    signal = Hourly_MACD_Signal(accnt=hkdb.accnt, symbol=symbol, hkdb=hkdb)
    hourly_ts = start_ts
    buys = []
    sells = []
    while hourly_ts <= end_ts:
        hourly_ts += hkdb.accnt.hours_to_ts(1)
        signal.hourly_update(hourly_ts)
        if signal.hourly_buy_signal():
            buys.append(hourly_ts)
        elif signal.hourly_sell_signal():
            sells.append(hourly_ts)
    print(buys)
    print(sells)


def train_model(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    df_train = hkdb.get_pandas_daily_klines(symbol, train_start_ts, train_end_ts)
    window_size = 10
    episode_count = 1000
    #scaler = MinMaxScaler(feature_range=(0, 1))
    #data = scaler.fit_transform(df_train['close'].values.reshape(-1, 1)).reshape(1, -1)[0].tolist()
    data = df_train['close'].values.tolist()
    l = len(data) - 1
    batch_size = 32
    agent = DQNAgent(state_size=window_size, pretrained=False, model_name=symbol)
    #agent.load()

    episode_start = agent.episode

    for e in xrange(episode_start, episode_count + 1):
        print("Episode " + str(e) + "/" + str(episode_count))
        state = getState(data, 0, window_size + 1)

        total_profit = 0
        agent.episode = e
        agent.inventory = []

        for t in xrange(l - window_size):
            action = agent.act(state)

            # sit
            next_state = getState(data, t + 1, window_size + 1)
            reward = 0

            if action == 1: # buy
                if len(agent.inventory) < agent.max_inventory:
                    agent.inventory.append(data[t])
                    #buy_price = scaler.inverse_transform([[data[t]]])[0][0]
                    #print("Buy: {}".format(buy_price))

            elif action == 2 and len(agent.inventory) > 0: # sell
                bought_price = agent.inventory.pop(0)
                reward = max(data[t] - bought_price, 0)
                total_profit += data[t] - bought_price
                #sell_price = scaler.inverse_transform([[data[t]]])[0][0]
                #buy_price = scaler.inverse_transform([[bought_price]])[0][0]
                #print("Sell: {} | Profit: {}".format(sell_price, sell_price - buy_price))

            done = True if t == l - window_size - 1 else False
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state

            if done:
                print("--------------------------------")
                #true_total_profit = scaler.inverse_transform([[total_profit]])[0][0]
                print("Total Profit: {}".format(total_profit))
                print("--------------------------------")

            if len(agent.memory) > batch_size:
                agent.train_experience_replay(batch_size)

        if e % 10 == 0:
            agent.save(e)


def eval_model(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    df_train = hkdb.get_pandas_daily_klines(symbol, test_start_ts, test_end_ts)
    window_size = 10
    #scaler = MinMaxScaler(feature_range=(0, 1))
    close_values = df_train['close'].values
    data = close_values.tolist() #scaler.fit_transform(df_train['close'].values.reshape(-1, 1)).reshape(1, -1)[0].tolist()
    l = len(data) - 1
    agent = DQNAgent(state_size=window_size, pretrained=True, model_name=symbol)
    #agent.load()

    total_profit = 0
    agent.inventory = []
    state = getState(data, 0, window_size + 1)

    buy_indices = []
    sell_indices = []

    for t in xrange(l - window_size):
        action = agent.act(state)

        # sit
        next_state = getState(data, t + 1, window_size + 1)
        reward = 0

        if action == 1: # buy
            if len(agent.inventory) < agent.max_inventory:
                agent.inventory.append(data[t])
                buy_price = data[t] #scaler.inverse_transform([[data[t]]])[0][0]
                print("Buy: {}".format(buy_price))
                buy_indices.append(t)

        elif action == 2 and len(agent.inventory) > 0: # sell
            bought_price = agent.inventory.pop(0)
            reward = max(data[t] - bought_price, 0)
            total_profit += data[t] - bought_price
            sell_price = data[t] #scaler.inverse_transform([[data[t]]])[0][0]
            buy_price = bought_price #scaler.inverse_transform([[bought_price]])[0][0]
            print("Sell: {} | Profit: {}".format(sell_price, sell_price - buy_price))
            sell_indices.append(t)

        done = True if t == l - window_size - 1 else False
        agent.memory.append((state, action, reward, next_state, done))
        state = next_state

        if done:
            print("--------------------------------")
            #true_total_profit = scaler.inverse_transform([[total_profit]])[0][0]
            print("Total Profit: {}".format(total_profit))
            print("--------------------------------")

    plt.subplot(211)
    for i in buy_indices:
        plt.axvline(x=i, color='green')
    for i in sell_indices:
        plt.axvline(x=i, color='red')
    symprice, = plt.plot(close_values, label=symbol)
    plt.legend(handles=[symprice])
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

    parser.add_argument('-t', action='store_true', dest='train',
                        default=False,
                        help='train model')

    parser.add_argument('-v', action='store_true', dest='verify',
                        default=False,
                        help='verify model')

    results = parser.parse_args()
    if not results.symbol:
        parser.print_help()
        sys.exit(0)

    accnt = AccountBinance(None, simulation=True)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)
    logFormatter = logging.Formatter("%(message)s")
    logger = logging.getLogger()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    hkdb = HourlyKlinesDB(accnt, results.hourly_filename, logger=logger)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = hkdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = hkdb.get_table_start_ts(results.symbol)
    print(train_start_ts)
    train_end_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index)
    test_start_ts = hkdb.get_table_ts_by_offset(results.symbol, train_end_index + 1)
    test_end_ts = hkdb.get_table_end_ts(results.symbol)

    enable_gpu = False
    device_types = []
    for device in device_lib.list_local_devices():
        device_types.append(device.device_type)
    if 'GPU' in device_types or 'XLA_GPU' in device_types:
        enable_gpu = True
    if enable_gpu:
        print("GPU detected, enabling tensorflow GPU...")
        config = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 8})
        sess = tf.Session(config=config)
        keras.backend.set_session(sess)

    train = True
    if results.verify:
        train = False
    if results.symbol:
        run_expert_signal(hkdb, results.symbol, train_start_ts, train_end_ts)
        #if train:
        #    train_model(hkdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
        #else:
        #    eval_model(hkdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
    else:
        parser.print_help()
    hkdb.close()
