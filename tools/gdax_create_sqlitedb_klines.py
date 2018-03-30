#!/usr/bin/python

#from pymongo import MongoClient
import os.path
import time
import sys
#from gdax.myhelpers import *
from trader import gdax
import sqlite3
import os.path
from datetime import datetime, timedelta
# kline format is list with the following 6 items:
# time bucket start time
# low lowest price during the bucket interval
# high highest price during the bucket interval
# open opening price (first trade) in the bucket interval
# close closing price (last trade) in the bucket interval
# volume volume of trading activity during the bucket interval

def get_klines_hours(pc, ticker_id, start, hours=4):
    end = (start + timedelta(hours=hours))
    return pc.get_product_historic_rates(ticker_id, start.isoformat(), end.isoformat(), 60)

def get_klines_days(pc, ticker_id, start, days=1):
    end = (start + timedelta(days=days))
    return pc.get_product_historic_rates(ticker_id, start.isoformat(), end.isoformat(), 86400)

def get_timestamp_range(c):
    q = "SELECT timestamp FROM klines ORDER BY timestamp ASC"
    c.execute(str(q))
    startts = datetime.fromtimestamp(int(c.fetchone()[0]))
    q = "SELECT timestamp FROM klines ORDER BY timestamp DESC"
    c.execute(str(q))
    endts = datetime.fromtimestamp(int(c.fetchone()[0]))
    return startts, endts

def create_update_klines_minutes(c, file_exists):
    if not file_exists:
        c.execute(
            '''create table if not exists klines (timestamp int, low real, high real, open real, close real, volume real)''')
        end = datetime.utcnow()
        start = (end - timedelta(weeks=(4 * 12)))
        current = start
    else:
        startts, endts = get_timestamp_range(c)
        end = datetime.utcnow()
        start = endts + timedelta(hours=4)
        current = start

    count = 0

    while current < end:
        klines = get_klines_hours(pc, ticker_id, current)
        if 'message' in klines:
            print(klines)
            time.sleep(1)
            continue
        for k in klines:
            c.execute("INSERT INTO klines VALUES ('{}', {}, {}, {}, {}, {})".format(k[0], k[1], k[2], k[3], k[4], k[5]))
        current = current + timedelta(hours=4)
        count += 4
        if count >= 12:
            count = 0
            time.sleep(1)

def create_update_klines_days(c):
    c.execute('''create table if not exists klines_days (timestamp int, low real, high real, open real, close real, volume real)''')
    end = datetime.utcnow()
    start = (end - timedelta(days=365*3))
    current = start

    startts, endts = get_timestamp_range(c)
    end = datetime.utcnow()
    start = endts + timedelta(days=7)
    current = start

    count = 0

    print("Retrieving klines...")

    while current < end:
        klines = get_klines_days(pc, ticker_id, current, days=7)
        for kline in klines:
            print('SELECT * FROM klines_days WHERE timestamp={}'.format(kline[0]))
            c.execute('SELECT * FROM klines_days WHERE timestamp={}'.format(kline[0]))
            print(c.rowcount)

        if 'message' in klines:
            print(klines)
            time.sleep(1)
            continue
        for k in klines:
            print("INSERT INTO klines_days VALUES ({}, {}, {}, {}, {}, {})".format(k[0], k[1], k[2], k[3], k[4], k[5]))
            c.execute("INSERT INTO klines_days VALUES ({}, {}, {}, {}, {}, {})".format(k[0], k[1], k[2], k[3], k[4], k[5]))
        print(current)
        current = current + timedelta(days=7)
        count += 7
        if count >= 36:
            count = 0
            time.sleep(1)


if __name__ == '__main__':
        ticker_id = 'BTC-USD'
        filename = '{}_klines.db'.format(ticker_id.replace('-', '_'))
        file_exists = os.path.exists(filename)

        pc = gdax.PublicClient()
        conn = sqlite3.connect(filename)

        c = conn.cursor()
        #create_update_klines_minutes(c, file_exists)
        create_update_klines_days(c)

        conn.commit()
        conn.close()
