#!/usr/bin/python
import os
import sys
import tweepy
import requests
import numpy as np
import sqlite3
import os.path
import matplotlib.pyplot as plt
import scipy
from scipy.fftpack import fft, ifft
from scipy import signal
import pywt
#import pywt.thresholding

def build_dataset(c):
    open_prices = []
    price_changes = []
    volumes = []
    q = "SELECT * FROM klines_days ORDER BY timestamp ASC"
    c.execute(str(q))
    last_openprice = 0.0
    last_volume = 0.0
    last_pricechange = 0.0
    pricechange = 0.0

    for row in c:
        timestamp, low, high, openprice, closeprice, volume = row
        if last_openprice != 0.0 and last_volume != 0.0:
            openprice = float(openprice)
            closeprice = float(closeprice)
            pricechange = closeprice - openprice
            volume = float(volume)
            open_prices.append(openprice) #(last_openprice - openprice) / last_openprice)
            if last_pricechange != 0.0:
                price_changes.append((last_pricechange - pricechange) / last_pricechange)
            #volumes.append((last_volume - volume) / last_volume)
        last_openprice = float(openprice)
        last_volume = float(volume)
        last_pricechange = pricechange
    return open_prices, price_changes #, volumes

if __name__ == '__main__':
    ticker_id = 'BTC-USD'
    basefile = ticker_id.replace('-', '_')

    conn = sqlite3.connect('{}_klines.db'.format(basefile))
    c = conn.cursor()

    open_prices, price_changes = build_dataset(c)
    conn.close()

    #fft_values = fft(open_prices)
    #b, a = signal.butter(5, 0.25)
    #y = signal.filtfilt(b, a, open_prices) #fft_values)

    #(ca, cd) = pywt.dwt(open_prices, 'haar')

    #cat = pywt.thresholding.soft(ca, np.std(ca) / 2)
    #cdt = pywt.thresholding.soft(cd, np.std(cd) / 2)

    #ts_rec = pywt.idwt(cat, cdt, 'haar')

    plt.plot(open_prices)
    #plt.plot(ts_rec)
    #plt.plot(y)
    #plt.plot(y)#open_prices)
    #plt.plot(volumes)
    plt.show()
