import sqlite3

class HourlyKlinesDB(object):
    def __init__(self, client, filename):
        self.client = client
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        # column names
        self.cnames = "ts, open, high, low, close, base_volume, quote_volume, trade_count, taker_buy_base_volume, taker_buy_quote_volume"

    def close(self):
        if self.conn:
            self.conn.close()

    def get_table_list(self):
        result = []
        res = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for name in res:
            result.append(name[0])
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

    def get_raw_klines_through_ts(self, symbol, end_ts):
        result = []
        cnames = "ts, open, high, low, close, base_volume, quote_volume"
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(cnames, symbol))
        for row in cur:
            result.append(row)
            if row[0] >= end_ts:
                break
        return result

    def get_dict_klines_through_ts(self, symbol, end_ts):
        result = []
        cnames = "ts, open, high, low, close, base_volume, quote_volume"
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {}".format(cnames, symbol))
        for row in cur:
            msg = {}
            for i in range(0, len(cnames)):
                msg[cnames[i]] = row[i]
            result.append(msg)
            if row[0] >= end_ts:
                break
        return result
