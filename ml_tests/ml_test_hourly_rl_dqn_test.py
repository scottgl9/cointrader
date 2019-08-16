#!/usr/bin/python
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
import numpy as np
from trader.lib.MachineLearning.DQNAgent import DQNAgent
from sklearn.preprocessing import MinMaxScaler

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# prints formatted price
def formatPrice(n):
    return ("-$" if n < 0 else "$") + "{0:.2f}".format(abs(n))


# returns the sigmoid
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# returns an an n-day state representation ending at time t
def getState(data, t, n):
    #d = t - n + 1
    #block = data[d:t + 1] if d >= 0 else -d * [data[0]] + data[0:t + 1]  # pad with t0
    block = data[t:t + n]
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


def simulate(hkdb, symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts, train=True):
    df_train = hkdb.get_pandas_daily_klines(symbol, train_start_ts, train_end_ts)
    window_size = 10
    episode_count = 1000
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(df_train['close'].values.reshape(-1, 1)).reshape(1, -1)[0].tolist()
    #df_test = hkdb.get_pandas_klines(symbol, test_start_ts, test_end_ts)
    l = len(data) - 1
    batch_size = 32
    agent = DQNAgent(state_size=window_size, action_size=3)

    for e in xrange(episode_count + 1):
        print "Episode " + str(e) + "/" + str(episode_count)
        state = getState(data, 0, window_size + 1)

        total_profit = 0
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
                #print "Sell: {}" + formatPrice(data[t]) + " | Profit: " + formatPrice(data[t] - bought_price)

            done = True if t == l - window_size - 1 else False
            agent.memory.append((state, action, reward, next_state, done))
            state = next_state

            if done:
                print "--------------------------------"
                true_total_profit = scaler.inverse_transform([[total_profit]])[0][0]
                print "Total Profit: {}".format(true_total_profit)
                print "--------------------------------"

            if len(agent.memory) > batch_size:
                agent.replay(batch_size)

        if e % 10 == 0:
            model_path = "models/model_ep" + str(e)
            print("Saving {}".format(model_path))
            agent.model.save(model_path)


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

    hkdb = HourlyKlinesDB(accnt, results.hourly_filename, None)
    print("Loading {}".format(results.hourly_filename))

    total_row_count = hkdb.get_table_row_count(results.symbol)
    train_end_index = int(total_row_count * float(results.split_percent) / 100.0)

    train_start_ts = hkdb.get_table_start_ts(results.symbol)
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
        simulate(hkdb, results.symbol, train_start_ts, train_end_ts, test_start_ts, test_end_ts, train)
    else:
        parser.print_help()
    hkdb.close()
