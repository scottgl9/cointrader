# Keep track of all executed buy orders which don't yet have corresponding sell orders
# This allows us to restore the state of the MultiTrader even if it exits prematurely

import sqlite3
import os.path
import sys

class TraderDB(object):
    def __init__(self, filename, logger=None):
        self.db = None
        self.filename = filename
        self.logger = logger


    def connect(self):
        exists = False
        if os.path.exists(self.filename):
            exists = True

        self.db = self.create_db_connection(self.filename)

        if not exists:
            self.create_table()
        else:
            self.remove_duplicate_trades()


    def remove_duplicate_trades(self):
        trades = self.get_all_trades()

        if len(trades) == 0:
            return

        timestamps = []

        for i in range(0, len(trades) - 1):
            t1 = trades[i]
            for j in range(i+1, len(trades) - 1):
                t2 = trades[j]
                if (t1['symbol'] == t2['symbol'] and
                    t1['sigid'] == t2['sigid'] and
                    t1['sigoid'] == t2['sigoid']):
                        timestamps.append(t2['ts'])
                        break
        for ts in timestamps:
            self.remove_trade_by_ts(ts)

        count = len(timestamps)
        if count != 0:
            self.logger.info("{} duplicate trades removed".format(count))


    def get_all_trades(self):
        trades = []
        if not self.db:
            return trades
        if self.get_trade_count_total() == 0:
            return trades

        cur = self.db.cursor()
        sql = """SELECT ts,symbol,price,qty,bought,sigid,sigoid from trades ORDER by ts DESC"""
        cur.execute(sql)
        for row in cur:
            trade = {}
            trade['ts'] = row[0]
            trade['symbol'] = row[1]
            trade['price'] = row[2]
            trade['qty'] = row[3]
            trade['bought'] = row[4]
            trade['sigid'] = row[5]
            trade['sigoid'] = row[6]
            trades.append(trade)
        return trades


    def get_trades(self, symbol):
        trades = []
        if not self.db:
            return trades
        if self.get_trade_count_total() == 0:
            return trades

        sql = """SELECT ts,symbol,price,qty,bought,sigid,sigoid from trades WHERE symbol='{}' ORDER BY ts DESC""".format(symbol)
        cur = self.db.cursor()
        cur.execute(sql)
        for row in cur:
            trade = {}
            trade['ts'] = row[0]
            trade['symbol'] = row[1]
            trade['price'] = row[2]
            trade['qty'] = row[3]
            trade['bought'] = row[4]
            trade['sigid'] = row[5]
            trade['sigoid'] = row[6]
            trades.append(trade)
        return trades


    def get_trade_count_total(self):
        count = 0
        if not self.db:
            return count

        cur = self.db.cursor()
        try:
            count = int(cur.execute("""SELECT COUNT(*) FROM trades""").fetchone()[0])
        except sqlite3.OperationalError:
            pass

        return count

    def get_trade_count(self, symbol, sig_id=0, sig_oid=0):
        count = 0
        if not self.db:
            return count

        sql = "SELECT COUNT(*) FROM trades WHERE symbol='{}'".format(symbol)
        if sig_id != 0:
            sql += " AND sigid={}".format(sig_id)
        if sig_oid != 0:
            sql += " AND sigoid={}".format(sig_oid)

        cur = self.db.cursor()

        try:
            count = int(cur.execute(sql).fetchone()[0])
        except sqlite3.OperationalError:
            pass

        return count

    def insert_trade(self, ts, symbol, price, qty, bought=True, sig_id=0, sig_oid=0):
        if not self.db:
            return

        count = self.get_trade_count(symbol, sig_id)
        if count > 0:
            self.remove_trade(symbol, sig_id)

        values = [ts, symbol, price, qty, bought, sig_id, sig_oid]
        cur = self.db.cursor()
        sql = """INSERT INTO trades (ts, symbol, price, qty, bought, sigid) values(?, ?, ?, ?, ?, ?, ?)"""
        try:
            cur.execute(sql, values)
            self.db.commit()
        except sqlite3.OperationalError:
            if self.logger:
                self.logger.info("FAILED to insert {} into {}".format(symbol, self.filename))


    def remove_trade_by_ts(self, ts):
        if not self.db:
            return
        if self.get_trade_count_total() == 0:
            return

        cur = self.db.cursor()
        sql = """DELETE FROM trades WHERE ts={}""".format(ts)
        try:
            cur.execute(sql)
            self.db.commit()
        except sqlite3.OperationalError:
            if self.logger:
                self.logger.warning("FAILED to remove ts={} from {}".format(ts, self.filename))


    def remove_trade(self, symbol, sig_id=0, sig_oid=0):
        if not self.db:
            return
        if self.get_trade_count_total() == 0:
            return

        sql = "DELETE FROM trades WHERE symbol='{}'".format(symbol)
        if sig_id != 0:
            sql += " AND sigid={}".format(sig_id)
        if sig_oid != 0:
            sql += " AND sigoid={}".format(sig_oid)

        cur = self.db.cursor()

        try:
            cur.execute(sql)
            self.db.commit()
        except sqlite3.OperationalError:
            if self.logger:
                self.logger.warning("FAILED to remove {} from {}".format(symbol, self.filename))


    def create_db_connection(self, filename):
        try:
            conn = sqlite3.connect(filename, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None


    def create_table(self):
        cur = self.db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS trades (id integer, ts integer, symbol text, price real, qty real, bought boolean, sigid integer, sigoid integer)"""
        cur.execute(sql)
        self.db.commit()


    def close(self):
        if self.db:
            self.db.close()
            self.db = None
