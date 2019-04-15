import sqlite3

class HourlyKlinesDB(object):
    def __init__(self, client, filename):
        self.client = client
        self.filename = filename
        self.conn = sqlite3.connect(filename)

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
