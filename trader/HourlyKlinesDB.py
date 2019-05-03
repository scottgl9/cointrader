# Manage hourly klines sqlite DB

import os
import sqlite3
import time
from datetime import datetime
from trader.lib.Kline import Kline
import pandas as pd
#from trader.account.binance.client import Client


class HourlyKlinesDB(object):
    def __init__(self, accnt, filename, symbol=None, logger=None):
        self.accnt = accnt
        self.filename = filename
        self.logger = logger
        self.symbol = symbol
        if self.symbol and not self.symbol_in_table_list(self.symbol):
            return

        if not filename or not os.path.exists(filename):
            raise IOError
        self.conn = sqlite3.connect(filename)
        # column names
        self.cnames_list = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume',
                            'trade_count', 'taker_buy_base_volume', 'taker_buy_quote_volume']
        self.cnames = ','.join(self.cnames_list)

        # short list column names
        self.scname_list = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume']
        self.scnames = ','.join(self.scname_list)
        self.table_symbols = self.get_table_list()
        self.table_last_update_ts = None
        if not self.accnt.simulate:
            self.table_last_update_ts = {}
            if not self.symbol:
                for symbol in self.table_symbols:
                    self.table_last_update_ts[symbol] = 0
            else:
                self.table_last_update_ts[self.symbol] = self.get_table_end_ts(self.symbol)


    # close connection to db
    def close(self):
        if self.conn:
            self.conn.close()

    def symbol_in_table_list(self, symbol):
        if symbol in self.table_symbols:
            return True
        return False

    # update all tables' hourly values ending in end_ts,
    # or if end_ts is zero, through the current time
    def update_all_tables(self, end_ts=0):
        result = 0
        last_ts = 0

        if not end_ts:
            end_ts = int(time.mktime(datetime.today().timetuple()) * 1000.0)

        for symbol in self.get_table_list():
            last_ts = self.update_table(symbol, end_ts)
            if last_ts:
                result = last_ts
        return result

    def get_last_update_ts(self, symbol):
        try:
            return self.table_last_update_ts[symbol]
        except KeyError:
            return

    def set_last_update_ts(self, symbol, hourly_ts):
        try:
            self.table_last_update_ts[symbol] = hourly_ts
        except KeyError:
            return

    # get list of tables named by trading symbol
    def get_table_list(self):
        result = []
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for name in res:
            result.append(name[0])
        return result

    # determine if timestamp already exists in table
    def ts_in_table(self, symbol, ts):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} WHERE ts = {}".format(symbol, ts))
        row = cur.fetchone()
        if row is None or not len(row):
            return False
        return True

    # update hourly values missing in table through end_ts
    def update_table(self, symbol, end_ts=0):
        last_ts = 0
        if not self.accnt:
            return 0
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
        result = cur.fetchone()
        start_ts = int(result[0])

        if not end_ts:
            end_ts = int(time.mktime(datetime.today().timetuple()) * 1000.0)

        end_ts = self.accnt.get_hourly_ts(end_ts)
        klines = self.accnt.get_hourly_klines(symbol, start_ts, end_ts)

        sql = """INSERT INTO {} ({}) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(symbol, self.cnames)

        count = 0

        for k in klines:
            if int(k[0]) == start_ts:
                continue
            if self.ts_in_table(symbol, int(k[0])):
                continue
            last_ts = int(k[0])
            del k[6]
            k = k[:-1]
            cur = self.conn.cursor()
            cur.execute(sql, k)
            count += 1

        if count:
            if last_ts:
                self.set_last_update_ts(symbol, last_ts)
            self.conn.commit()

        return last_ts

    # return list of specific kline column by specifying which column to select
    def get_kline_values_by_column(self, symbol, column='close', end_ts=0):
        result = []
        cindex = self.cnames.index(column)
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {} ORDER by ts ASC".format(self.scnames, symbol))
        for row in cur:
            result.append(row[cindex])
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get first timestamp in symbol table
    def get_table_start_ts(self, symbol):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(symbol))
        result = cur.fetchone()
        return int(result[0])

    # get last timestamp in symbol table
    def get_table_end_ts(self, symbol):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
        result = cur.fetchone()
        return int(result[0])

    # get range of timestamps for table with name symbol
    def get_table_ts_range(self, symbol):
        start_ts = self.get_table_start_ts(symbol)
        end_ts = self.get_table_end_ts(symbol)
        return start_ts, end_ts

    def build_sql_select_query(self, symbol, start_ts, end_ts):
        sql = "SELECT {} FROM {} ".format(self.scnames, symbol)

        if start_ts and end_ts:
            sql += "WHERE ts >= {} AND ts <= {} ".format(start_ts, end_ts)
        elif not start_ts and end_ts:
            sql += "WHERE ts <= {} ".format(end_ts)
        elif start_ts and not end_ts:
            sql += "WHERE {} <= ts ".format(start_ts)

        sql += "ORDER BY ts ASC"
        return sql

    # get klines as list of rows from db table
    def get_raw_klines(self, symbol, start_ts=0, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {} ORDER BY ts ASC".format(self.scnames, symbol))
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
            result.append(row)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get klines as list of dicts from db table
    def get_dict_klines(self, symbol, start_ts=0, end_ts=0):
        result = []
        cur = self.conn.cursor()

        sql = self.build_sql_select_query(symbol, start_ts, end_ts)

        cur.execute(sql)
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
            msg = {}
            for i in range(0, len(self.scname_list)):
                msg[self.scname_list[i]] = row[i]
            result.append(msg)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # load single hourly kline in dict format
    def get_dict_kline(self, symbol, hourly_ts=0):
        sql = "SELECT {} FROM {} WHERE ts = {}".format(self.scnames, symbol, hourly_ts)
        cur = self.conn.cursor()
        cur.execute(sql)
        k = cur.fetchone()

        result = {}
        for i in range(0, len(self.scname_list)):
            result[self.scname_list[i]] = k[i]
        return result

    # load hourly klines in pandas dataframe
    def get_pandas_klines(self, symbol, start_ts=0, end_ts=0):
        sql = self.build_sql_select_query(symbol, start_ts, end_ts)

        result = pd.read_sql_query(sql, self.conn)
        return result

    # load single hourly kline in pandas dataframe
    def get_pandas_kline(self, symbol, hourly_ts=0):
        sql = "SELECT {} FROM {} WHERE ts = {}".format(self.scnames, symbol, hourly_ts)
        result = pd.read_sql_query(sql, self.conn)
        return result

    # get klines as list of Kline class from db table
    def get_klines(self, symbol, start_ts=0, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {} ORDER BY ts ASC".format(self.scnames, symbol))
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
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
