#!/usr/bin/env python3
# test HourlyLSTM class
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
import sys
import os
import math
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.binance.AccountBinance import AccountBinance
import keras
import tensorflow as tf
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np
import random
from collections import deque

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


# returns the sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


class Agent(object):
    def __init__(self, state_size, max_inventory=1, is_eval=False, model_name=""):
        self.state_size = state_size # normalized previous days
        self.action_size = 3 # sit, buy, sell
        self.memory = deque(maxlen=100000)
        self.inventory = []
        self.max_inventory = max_inventory
        self.model_name = model_name
        self.is_eval = is_eval

        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        self.model = load_model("models/" + model_name) if is_eval else self._model()

    def _model(self):
        model = Sequential()
        model.add(Dense(units=64, input_dim=self.state_size, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(units=8, activation="relu"))
        model.add(Dense(self.action_size, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))

        return model

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        options = self.model.predict(state)
        return np.argmax(options[0])

    # returns an an n-day state representation ending at time t
    def getState(self, data, t, n):
        d = t - n + 1
        block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
        res = []
        for i in xrange(n - 1):
            delta = float(block[i + 1] - block[i])
            try:
                res.append(sigmoid(delta))
            except OverflowError:
                print("ERROR: sigmoid({})".format(delta))
                res.append(float('inf'))
                #sys.exit(-1)

        return np.array([res])

    def expReplay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in xrange(l - batch_size + 1, l):
            mini_batch.append(self.memory[i])

        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])

            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay 


def simulate(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts, train=True):
    df_train = kdb.get_pandas_daily_klines(symbol, train_start_ts, train_end_ts)
    window_size = 10
    episode_count = 1000
    data = df_train['close'].values.tolist()
    #df_test = kdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    l = len(data) - 1
    batch_size = 32
    agent = Agent(window_size)

    for e in xrange(episode_count + 1):
        print("Episode " + str(e) + "/" + str(episode_count))
        state = agent.getState(data, 0, window_size + 1)

        total_profit = 0
        agent.inventory = []

        for t in xrange(l):
            action = agent.act(state)

            # sit
            next_state = agent.getState(data, t + 1, window_size + 1)
            reward = 0

            if action == 1: # buy
                if len(agent.inventory) < agent.max_inventory:
                    agent.inventory.append(data[t])
                    print("Buy: " + formatPrice(data[t]))

            elif action == 2 and len(agent.inventory) > 0: # sell
                bought_price = agent.inventory.pop(0)
                reward = max(data[t] - bought_price, 0)
                total_profit += data[t] - bought_price
                print("Sell: " + formatPrice(data[t]) + " | Profit: " + formatPrice(data[t] - bought_price))

            done = True if t == l - 1 else False
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state

            if done:
                print("--------------------------------")
                print("Total Profit: " + formatPrice(total_profit))
                print("--------------------------------")

            if len(agent.memory) > batch_size:
                agent.expReplay(batch_size)

        if e % 10 == 0:
            model_path = "models/model_ep" + str(e)
            print("Saving {}".format(model_path))
            agent.model.save(model_path)


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

    kdb = KlinesDB(accnt, results.hourly_filename, None)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = kdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = kdb.get_table_start_ts(results.symbol)
    train_end_ts = kdb.get_table_ts_by_offset(results.symbol, train_end_index)
    test_start_ts = kdb.get_table_ts_by_offset(results.symbol, train_end_index + 1)
    test_end_ts = kdb.get_table_end_ts(results.symbol)

    config = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 8})
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    train = True
    if results.verify:
        train = False
    if results.symbol:
        simulate(kdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts, train)
    else:
        parser.print_help()
    kdb.close()
