#!/usr/bin/env python3
# test HourlyLSTM class
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader
import sys
import math
import matplotlib.pyplot as plt
import argparse
from trader.KlinesDB import KlinesDB
from trader.account.binance.AccountBinance import AccountBinance
import tensorflow as tf
from tensorflow.python.client import device_lib
from trader.lib.MachineLearning.DQNAgent import DQNAgent
from sklearn.preprocessing import MinMaxScaler
import os
import numpy as np
import random
from collections import deque
from keras.layers import Dense, Input
from keras.optimizers import Adam
from keras.utils import to_categorical
import keras

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Deep Q-learning Agent
class DQNAgent(object):
    def __init__(self, symbol, state_size, action_size, is_eval=False, max_inventory=1):
        self.symbol = symbol
        self.episode = 0
        self.weights_path = "models/{}.h5".format(symbol)
        self.episode_path = "models/{}.txt".format(symbol)
        self.is_eval = is_eval
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.inventory = []
        self.max_inventory = max_inventory
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        # model = Sequential()
        # model.add(Dense(24, input_shape=(self.state_size,), activation='relu'))
        # model.add(Dense(24, activation='relu'))
        # model.add(Dense(self.action_size, activation='linear'))
        # model.compile(loss='mse',
        #               optimizer=Adam(lr=self.learning_rate))
        input_layer = Input((self.state_size,), batch_shape=(None, 1, self.state_size))
        actions_input = keras.layers.Input((self.action_size,), name='mask')
        hl = Dense(24, activation="relu")(input_layer)
        h2 = Dense(24, activation="relu")(hl)
        h3 = Dense(24, activation="relu")(h2)
        output_layer = Dense(self.action_size, activation="linear")(h3)
        filtered_output = keras.layers.multiply([output_layer, actions_input])
        model = keras.models.Model(input=[input_layer, actions_input], output=filtered_output) #Model(input_layer, output_layer)
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model

    def load_weights(self):
        self.model.load_weights(self.weights_path)

    def save_weights(self):
        self.model.save_weights(self.weights_path, overwrite=True)

    def load(self):
        if not os.path.exists(self.episode_path):
            return 0
        with open(self.episode_path, 'r') as f:
            self.episode = int(f.readline().strip()) + 1
        self.load_weights()
        print("Loaded episode {}".format(self.episode))
        return self.episode

    def save(self):
        with open(self.episode_path, 'w') as f:
            f.write(str(self.episode))
        self.save_weights()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        action_mask = np.ones((1, self.action_size))
        act_values = self.model.predict([state[0].reshape(1, 1, self.state_size), action_mask], batch_size=1)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        idx = np.random.choice(len(self.memory), size=batch_size, replace=False)
        minibatch = np.array(self.memory)[idx]

        # Extract the columns from our sample
        states = np.array(list(minibatch[:, 0]))
        actions = minibatch[:, 1]
        rewards = np.array(minibatch[:, 2])
        next_states = np.array(list(minibatch[:, 3]))
        is_terminal = minibatch[:, 4].tolist()

        action_mask = np.ones((len(next_states), self.action_size))
        # First, predict the Q values of the next states. Note how we are passing ones as the mask.
        next_Q_values = self.model.predict([next_states, action_mask])

        # The Q values of the terminal states is 0 by definition, so override them
        next_Q_values[is_terminal] = 0

        # actions one hot encoded
        actions_encoded = to_categorical(actions, num_classes=3)

        # fix the shape of next_Q_values
        next_Q_values = next_Q_values.reshape(batch_size, self.action_size)
        # The Q values of each start state is the reward + gamma * the max next state Q value
        Q_values = rewards + self.gamma * np.amax(next_Q_values, axis=1)

        targets = actions_encoded * Q_values[:, None]
        targets = targets.reshape(batch_size, 1, self.action_size)

        # Fit the keras model. Note how we are passing the actions as the mask and multiplying
        # the targets by the actions.
        self.model.fit(
            [states, actions_encoded], targets,
            nb_epoch=1, batch_size=len(states), verbose=0
        )
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


# returns the sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# returns an an n-day state representation ending at time t
def getState(data, t, n):
    d = t - n + 1
    block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
    #block = data[t:t + n]
    res = []
    for i in xrange(n - 1):
        delta = float(block[i + 1] - block[i])
        res.append(delta)
        #try:
        #    #print(sigmoid(delta))
        #    res.append(sigmoid(delta))
        #except OverflowError:
        #    print("ERROR: sigmoid({})".format(delta))
        #    res.append(float('inf'))
        #    #sys.exit(-1)

    return np.array([res])


def train_model(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    df_train = kdb.get_pandas_daily_klines(symbol, train_start_ts, train_end_ts)
    window_size = 10
    episode_count = 1000
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(df_train['close'].values.reshape(-1, 1)).reshape(1, -1)[0].tolist()
    #df_test = kdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    l = len(data) - 1
    batch_size = 32
    agent = DQNAgent(symbol, state_size=window_size, action_size=3, is_eval=False)
    agent.load()

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
                true_total_profit = scaler.inverse_transform([[total_profit]])[0][0]
                print("Total Profit: {}".format(true_total_profit))
                print("--------------------------------")

            if len(agent.memory) > batch_size:
                agent.replay(batch_size)

        agent.save()
        if e % 10 == 0:
            model_path = "models/model_ep" + str(e)
            print("Saving {}".format(model_path))
            agent.model.save(model_path)


def eval_model(kdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts):
    df_train = kdb.get_pandas_daily_klines(symbol, test_start_ts, test_end_ts)
    window_size = 10
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_values = df_train['close'].values
    data = scaler.fit_transform(df_train['close'].values.reshape(-1, 1)).reshape(1, -1)[0].tolist()
    l = len(data) - 1
    agent = DQNAgent(symbol, state_size=window_size, action_size=3, is_eval=True)
    agent.load()

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
                buy_price = scaler.inverse_transform([[data[t]]])[0][0]
                print("Buy: {}".format(buy_price))
                buy_indices.append(t)

        elif action == 2 and len(agent.inventory) > 0: # sell
            bought_price = agent.inventory.pop(0)
            reward = max(data[t] - bought_price, 0)
            total_profit += data[t] - bought_price
            sell_price = scaler.inverse_transform([[data[t]]])[0][0]
            buy_price = scaler.inverse_transform([[bought_price]])[0][0]
            print("Sell: {} | Profit: {}".format(sell_price, sell_price - buy_price))
            sell_indices.append(t)

        done = True if t == l - window_size - 1 else False
        agent.memory.append((state, action, reward, next_state, done))
        state = next_state

        if done:
            print("--------------------------------")
            true_total_profit = scaler.inverse_transform([[total_profit]])[0][0]
            print("Total Profit: {}".format(true_total_profit))
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
        if train:
            train_model(kdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
        else:
            eval_model(kdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts)
    else:
        parser.print_help()
    kdb.close()
