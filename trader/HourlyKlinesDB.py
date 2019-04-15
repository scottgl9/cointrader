# Manage hourly klines sqlite DB

import os
import sqlite3
import time
from datetime import datetime
from trader.lib.Kline import Kline
#from trader.account.binance.client import Client


class HourlyKlinesDB(object):
    def __init__(self, accnt, filename, logger=None):
        self.accnt = accnt
        self.filename = filename
        self.logger = logger
        if not filename or not os.path.exists(filename):
            raise IOError
        self.conn = sqlite3.connect(filename)
        # column names
        self.cnames = "ts, open, high, low, close, base_volume, quote_volume, trade_count, taker_buy_base_volume, taker_buy_quote_volume"
        # short list column names
        self.scnames = "ts, open, high, low, close, base_volume, quote_volume"

    # close connection to db
    def close(self):
        if self.conn:
            self.conn.close()

    # update all tables' hourly values ending in end_ts,
    # or if end_ts is zero, through the current time
    def update_all_tables(self, end_ts=0):
        if not end_ts:
            end_ts = int(time.mktime(datetime.today().timetuple()) * 1000.0)

        for symbol in self.get_table_list():
            self.update_table(symbol, end_ts)

    # get list of tables named by trading symbol
    def get_table_list(self):
        result = []
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for name in res:
            result.append(name[0])
        return result

    # update hourly values missing in table through end_ts
    def update_table(self, symbol, end_ts):
        if not self.accnt:
            return
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
        result = cur.fetchone()
        start_ts = result[0]
        # klines = self.client.get_historical_klines_generator(
        #     symbol=symbol,
        #     interval=Client.KLINE_INTERVAL_1HOUR,
        #     start_str=start_ts,
        #     end_str=end_ts,
        # )
        klines = self.accnt.get_hourly_klines(symbol, start_ts, end_ts)

        sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(symbol, self.cnames)

        for k in klines:
            if k[0] == start_ts:
                continue
            del k[6]
            k = k[:-1]
            cur = self.conn.cursor()
            cur.execute(sql, k)
        self.conn.commit()

    # return list of specific kline column by specifying which column to select
    def get_kline_values_by_column(self, symbol, column='close', end_ts=0):
        result = []
        cindex = self.cnames.index(column)
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(self.scnames, symbol))
        for row in cur:
            result.append(row[cindex])
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get range of timestamps for table with name symbol
    def get_table_ts_range(self, symbol):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
        result = cur.fetchone()
        end_ts = int(result[0] / 1000)
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(symbol))
        result = cur.fetchone()
        start_ts = int(result[0])
        return start_ts, end_ts

    # get klines as list of rows from db table
    def get_raw_klines_through_ts(self, symbol, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(self.scnames, symbol))
        for row in cur:
            result.append(row)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get klines as list of dicts from db table
    def get_dict_klines_through_ts(self, symbol, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(self.scnames, symbol))
        for row in cur:
            msg = {}
            for i in range(0, len(self.scnames)):
                msg[self.scnames[i]] = row[i]
            result.append(msg)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get klines as list of Kline class from db table
    def get_klines_through_ts(self, symbol, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(self.scnames, symbol))
        for row in cur:
            kline = Kline()
            kline.ts = row[0]
            kline.open = row[1]
            kline.high = row[2]
            kline.low = row[3]
            kline.close = row[4]
            kline.volume_base = row[5]
            kline.volume_quote = row[6]
            result.append(kline)
            if end_ts and row[0] >= end_ts:
                break
        return result
