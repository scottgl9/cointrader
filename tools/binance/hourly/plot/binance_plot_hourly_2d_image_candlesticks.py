#!/usr/bin/env python3
import sys
try:
    import trader
except ImportError:
    sys.path.append('.')
    import trader

import sqlite3
import sys
import os
from datetime import datetime
import time
from trader.account.binance.client import Client
from trader.config import *
import io
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import argparse
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.indicator.OBV import OBV
from trader.indicator.EMA import EMA


def plot_candlestick(draw, im, o, h, l, c, index, count, x_total_size, y_total_size):
    cs_size = int(x_total_size / count)
    draw.rectangle(xy=[index*cs_size, 1, (index+1)*cs_size, y_total_size-2], outline=0)
    #draw.line((0, 0) + im.size, fill=128)
    #plt.gca().add_patch(Rectangle((index*cs_size, 0), cs_size/2, y_total_size, linewidth=1, edgecolor='black', facecolor='none'))
    #plt.axvline(x=[index*cs_size + int(cs_size/4)], ymin=0, ymax=y_total_size)
    #plt.axvspan(xmin=index*cs_size, xmax=(index+1)*cs_size, ymin=20, ymax=y_total_size)


def simulate(hkdb, symbol, start_ts, end_ts):
    msgs = hkdb.get_dict_klines(symbol, start_ts, end_ts)

    close_prices = []
    open_prices = []
    low_prices = []
    high_prices = []
    volumes = []

    dpi = 80
    x_fig_size = 8
    y_fig_size = 1
    x_total_size = x_fig_size * dpi
    y_total_size = y_fig_size * dpi
    im = Image.new("RGB", (x_total_size, y_total_size), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    count = 8
    for i in range(0, count):
        close = float(msgs[i]['close'])
        low = float(msgs[i]['low'])
        high = float(msgs[i]['high'])
        open = float(msgs[i]['open'])
        plot_candlestick(draw, im, open, high, low, close, i, count, x_total_size, y_total_size)
    #plt.plot([1, 2])
    # plt.title("test")
    #plt.axis('off')
    #buf = io.BytesIO()
    #plt.savefig(buf, format='png')
    #buf.seek(0)
    #im = Image.open(buf)
    im.show()
    #buf.close()


# get first timestamp from kline sqlite db
def get_first_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E ASC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

def get_last_timestamp(filename, symbol):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #c.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
    c.execute("SELECT E FROM miniticker WHERE s='{}' ORDER BY E DESC LIMIT 1".format(symbol))
    result = c.fetchone()
    return int(result[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # used to get first timestamp for symbol from precaptured live market data
    parser.add_argument('-f', action='store', dest='filename',
                        default='',
                        help='filename of kline sqlite db')

    parser.add_argument('--hours', action='store', dest='hours',
                        default=48,
                        help='Hours before first ts in db specified by -f')

    parser.add_argument('-k', action='store', dest='hourly_filename',
                        default='binance_hourly_klines_BTC.db',
                        help='filename of hourly kline sqlite db')

    parser.add_argument('-s', action='store', dest='symbol',
                        default='',
                        help='trade symbol')

    parser.add_argument('-l', action='store_true', dest='list_table_names',
                        default=False,
                        help='List table names in db')

    parser.add_argument('--start-date', action='store', dest='start_date',
                        default='',
                        help='specify start date in month/day/year format')

    parser.add_argument('--end-date', action='store', dest='end_date',
                        default='',
                        help='specify end date in month/day/year format')

    results = parser.parse_args()


    hourly_filename = results.hourly_filename
    symbol = results.symbol
    start_ts = 0
    end_ts = 0

    if results.filename:
        if not os.path.exists(results.filename):
            print("file {} doesn't exist, exiting...".format(results.filename))
            sys.exit(-1)
        else:
            end_ts = get_last_timestamp(results.filename, symbol)
            start_ts = get_first_timestamp(results.filename, symbol)
            start_ts = start_ts - 1000 * 3600 * int(results.hours)
            print(start_ts, end_ts)
    elif results.start_date and results.end_date:
        start_dt = datetime.strptime(results.start_date, '%m/%d/%Y')
        end_dt = datetime.strptime(results.end_date, '%m/%d/%Y')
        start_ts = int(time.mktime(start_dt.timetuple()) * 1000.0)
        end_ts = int(time.mktime(end_dt.timetuple()) * 1000.0)

    if not os.path.exists(results.hourly_filename):
        print("file {} doesn't exist, exiting...".format(results.filename))
        sys.exit(-1)

    hkdb = HourlyKlinesDB(None, hourly_filename, None)
    print("Loading {}".format(hourly_filename))

    if results.list_table_names:
        for symbol in hkdb.get_table_list():
            print(symbol)

    if symbol:
        simulate(hkdb, symbol, start_ts, end_ts)
    else:
        parser.print_help()
    hkdb.close()