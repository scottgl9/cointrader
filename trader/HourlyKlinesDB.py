import sqlite3
from trader.lib.Kline import Kline

class HourlyKlinesDB(object):
    def __init__(self, client, filename):
        self.client = client
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        # column names
        self.cnames = "ts, open, high, low, close, base_volume, quote_volume, trade_count, taker_buy_base_volume, taker_buy_quote_volume"
        self.scnames = "ts, open, high, low, close, base_volume, quote_volume"

    def close(self):
        if self.conn:
            self.conn.close()

    def get_table_list(self):
        result = []
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for name in res:
            result.append(name[0])
        return result

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

    def get_table_ts_range(self, symbol):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
        result = cur.fetchone()
        end_ts = int(result[0] / 1000)
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(symbol))
        result = cur.fetchone()
        start_ts = int(result[0])
        return start_ts, end_ts

    def get_raw_klines_through_ts(self, symbol, end_ts=0):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(self.scnames, symbol))
        for row in cur:
            result.append(row)
            if end_ts and row[0] >= end_ts:
                break
        return result

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
