#!/usr/bin/python
import os
import sys
import tweepy
import requests
import numpy as np
import sqlite3
import os.path

from keras.models import Sequential, load_model
from keras.layers import Input, LSTM, Dense, Activation
from textblob import TextBlob


def build_dataset(c):
    trainX = []
    trainY = []
    open_prices = []
    q = "SELECT * FROM klines_days ORDER BY timestamp ASC"
    c.execute(str(q))
    last_openprice = 0.0
    last_volume = 0.0

    for row in c:
        timestamp, low, high, openprice, closeprice, volume = row
        if last_openprice != 0.0 and last_volume != 0.0:
            openprice = float(openprice)
            closeprice = float(closeprice)
            volume = float(volume)
            trainX.append(((last_openprice - openprice) / last_openprice)) #, volume))
            trainY.append(((last_openprice - openprice) / last_openprice))
            open_prices.append(openprice)
        last_openprice = float(openprice)
        last_volume = float(volume)
    return open_prices[1:], np.array(trainX[:-1]), np.array(trainY[1:])

if __name__ == '__main__':
    ticker_id = 'LTC-USD'
    basefile = ticker_id.replace('-', '_')

    conn = sqlite3.connect('{}_klines.db'.format(basefile))
    c = conn.cursor()

    open_prices, trainX, trainY = build_dataset(c)
    conn.close()

    if os.path.exists(basefile + '.h5'):
        model = load_model(basefile + '.h5')
    else:
        # Create and fit Multilinear Perceptron model
        model = Sequential()
        model.add(Dense(32, input_dim=1, activation='relu'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mean_squared_error', optimizer='adam')
        #model.compile(optimizer='sgd', loss='mse', metrics=["accuracy"])

        model.fit(trainX, trainY, nb_epoch=200, batch_size=2, verbose=2)
        model.save(basefile + '.h5')

    count = 0
    #last_price = np.array([trainX[-1]])
    #while count < 100:
    predicted_price = model.predict(np.array([trainX[-1]]))#last_price)[0][0]
    last_price = float(open_prices[-1]) * (1.0 + float(trainX[-1]))
    next_price = last_price * (1.0 + float(predicted_price[0][0]))
    print('The price will move from %s to %s' % (last_price, next_price))
    #last_price = np.array([predicted_price])
    #count += 1
