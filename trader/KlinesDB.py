# Manage hourly klines sqlite DB (formerly HourlyKlinesDB)
import os
import sqlite3
import time
from datetime import datetime
from trader.lib.struct.Kline import Kline
import pandas as pd


class KlinesDB(object):
    def __init__(self, accnt, filename, symbol=None, logger=None):
        self.accnt = accnt
        self.filename = filename
        self.logger = logger
        self.symbol = symbol

        if not filename or not os.path.exists(filename):
            raise IOError
        self.conn = sqlite3.connect(filename)
        # column names
        self.cnames_list = self.accnt.get_hourly_column_names()
        self.cnames = ','.join(self.cnames_list)
        self.fmt_values = ','.join(['?'] * len(self.cnames_list))

        self.table_symbols = self.get_table_list()
        self.table_last_update_ts = None

        if self.symbol and not self.symbol_in_table_list(self.symbol):
            return

        if self.accnt and not self.accnt.simulate:
            self.table_last_update_ts = {}
            if not self.symbol:
                for symbol in self.table_symbols:
                    self.table_last_update_ts[symbol] = self.get_table_end_ts(symbol)
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

        if not end_ts:
            end_ts = int(self.accnt.seconds_to_ts(time.mktime(datetime.today().timetuple())))

        for symbol in self.get_table_list():
            last_ts = self.update_table(symbol, end_ts)
            if last_ts:
                result = last_ts
        return result

    # iterate through all tables, and get latest hourly ts
    def get_latest_db_hourly_ts(self):
        latest_hourly_ts = 0
        cur = self.conn.cursor()
        for symbol in self.table_symbols:
            cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(symbol))
            result = cur.fetchone()
            ts = int(result[0])
            if ts > latest_hourly_ts:
                latest_hourly_ts = ts
        return latest_hourly_ts

    # get list of table names which are not up to date
    def get_outdated_table_names(self):
        result = []
        latest_hourly_ts = self.get_latest_db_hourly_ts()
        for symbol in self.table_symbols:
            if not self.ts_in_table(symbol, latest_hourly_ts):
                result.append(symbol)
        return result

    # remove outdated tables from sqlite db
    def remove_outdated_tables(self):
        cur = self.conn.cursor()
        symbols = self.get_outdated_table_names()
        for symbol in symbols:
            if self.logger:
                self.logger.info("Removing table {} from {}".format(symbol, self.filename))
            try:
                del self.table_last_update_ts[symbol]
            except (KeyError, TypeError):
                pass
            cur.execute("DROP TABLE {}".format(symbol))
        self.conn.commit()
        self.table_symbols = self.get_table_list()

    def get_last_update_ts(self, symbol):
        if not self.table_last_update_ts:
            return 0
        try:
            return self.table_last_update_ts[symbol]
        except KeyError:
            return 0

    def set_last_update_ts(self, symbol, hourly_ts):
        if not self.table_last_update_ts:
            return
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

    def get_table_row_count(self, symbol):
        table_name = self.get_table_from_symbol(symbol)
        res = self.conn.execute("SELECT count(*) FROM {}".format(table_name))
        return res.fetchone()[0]

    # determine if timestamp already exists in table
    def ts_in_table(self, symbol, ts):
        table_name = self.get_table_from_symbol(symbol)
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} WHERE ts = {}".format(table_name, ts))
        row = cur.fetchone()
        if row is None or not len(row):
            return False
        return True

    # update hourly values missing in table through end_ts
    def update_table(self, table_name, end_ts=0, fix_gaps=False):
        symbol = self.get_symbol_from_table(table_name)
        last_ts = 0
        if not self.accnt:
            return 0
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(table_name))
        result = cur.fetchone()
        start_ts = int(result[0])

        if not end_ts:
            end_ts = int(self.accnt.seconds_to_ts(time.mktime(datetime.today().timetuple())))

        # if ts already in table, do not add and return ts
        end_ts = self.accnt.get_hourly_ts(end_ts)
        if self.ts_in_table(table_name, end_ts):
            return end_ts

        klines = self.accnt.get_hourly_klines(symbol, start_ts, end_ts)
        if not len(klines):
            return end_ts
        #print(klines)

        sql = """INSERT INTO {} ({}) values({})""".format(table_name, self.cnames, self.fmt_values)

        count = 0
        cur = self.conn.cursor()

        ts_index = self.cnames.index('ts')

        last_ts = 0
        last_kline = None

        if fix_gaps:
            for k in klines:
                cur_ts = int(k[0])
                # skip if is not an hourly ts
                if not self.accnt.is_hourly_ts(cur_ts):
                    print("{}: skipping {}".format(symbol, cur_ts))
                    continue
                # check for gaps in hourly klines, for gaps fill with previous kline
                if last_kline and int(cur_ts - last_ts) != int(self.accnt.hours_to_ts(1)):
                    print("{}: gap from {} to {}, filling...".format(symbol, last_ts, cur_ts))
                    ts = last_ts + int(self.accnt.hours_to_ts(1))
                    while ts < cur_ts:
                        last_kline[0] = int(ts)
                        cur.execute(sql, last_kline)
                        ts += int(self.accnt.hours_to_ts(1))
                cur.execute(sql, k)
                count += 1
                last_ts = cur_ts
                last_kline = k
        else:
            for k in klines:
                if int(k[ts_index]) == start_ts:
                    continue
                if self.ts_in_table(table_name, int(k[ts_index])):
                    continue
                last_ts = int(k[ts_index])
                cur.execute(sql, k)
                count += 1

        if count:
            if last_ts:
                self.set_last_update_ts(symbol, last_ts)
            self.conn.commit()

        return last_ts

    def check_tables_duplicates(self):
        found = False
        for symbol in self.get_table_list():
            cur = self.conn.cursor()
            sql = "SELECT ts, COUNT(*) c FROM {} GROUP BY ts HAVING c > 1;".format(symbol)
            result = cur.execute(sql)
            count = 0
            for row in result:
                count += 1
            if count:
                print("{}: {} Duplicate entries found".format(symbol, count))
                found = True
        return found

    def check_duplicates(self, table_name):
        found = False
        cur = self.conn.cursor()
        sql = "SELECT ts, COUNT(*) c FROM {} GROUP BY ts HAVING c > 1;".format(table_name)
        result = cur.execute(sql)
        count = 0
        for row in result:
            count += 1
        if count:
            print("{}: {} Duplicate entries found".format(table_name, count))
            found = True
        return found

    # check hourly kline db table for any errors, return True if error(s) found
    def check_table(self, table_name):
        found = False
        if self.check_duplicates(table_name):
            found = True

        last_ts = 0
        cur = self.conn.cursor()
        result = cur.execute("SELECT ts from {}".format(table_name))
        for row in result:
            ts = int(row[0])
            if last_ts:
                delta_ts = int(self.accnt.ts_to_seconds(ts - last_ts))
                if delta_ts != 3600:
                    print("{}: invalid delta ts found {}".format(table_name, delta_ts))
                    found = True
            last_ts = ts
        return found

    def list_table_dates(self, table_name):
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(table_name))
        result = cur.fetchone()
        end_ts = int(self.accnt.ts_to_seconds(result[0]))
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(table_name))
        result = cur.fetchone()
        start_ts = int(self.accnt.ts_to_seconds(result[0]))

        start_date = time.ctime(start_ts)
        end_date = time.ctime(end_ts)
        if len(table_name) <= 5:
            print("{}: \t\t{} \t{}".format(table_name, start_date, end_date))
        else:
            print("{}: \t{} \t{}".format(table_name, start_date, end_date))

    # return list of specific kline column by specifying which column to select
    def get_kline_values_by_column(self, symbol, column='close', start_ts=0, end_ts=0):
        result = []
        cur = self.conn.cursor()
        sql = self.build_sql_select_field_query(symbol, column, start_ts, end_ts)
        cur.execute(sql)
        for row in cur:
            result.append(row[0])
        return result

    # if table name differs from symbol, translate symbol to table name
    def get_table_from_symbol(self, symbol):
        if self.accnt:
            table_name = self.accnt.get_hourly_table_name(symbol)
        else:
            table_name = symbol
        return table_name

    # if table name differs from symbol, translate table name to symbol
    def get_symbol_from_table(self, table_name):
        if self.accnt:
            symbol = self.accnt.get_symbol_hourly_table(table_name)
        else:
            symbol = table_name
        return symbol

    def get_table_ts_by_offset(self, symbol, offset=0):
        table_name = self.get_table_from_symbol(symbol)
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1 OFFSET {}".format(table_name, offset))
        result = cur.fetchone()
        return int(result[0])

    # get first timestamp in symbol table
    def get_table_start_ts(self, symbol):
        table_name = self.get_table_from_symbol(symbol)
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts ASC LIMIT 1".format(table_name))
        result = cur.fetchone()
        return int(result[0])

    # get last timestamp in symbol table
    def get_table_end_ts(self, symbol):
        table_name = self.get_table_from_symbol(symbol)
        cur = self.conn.cursor()
        cur.execute("SELECT ts FROM {} ORDER BY ts DESC LIMIT 1".format(table_name))
        result = cur.fetchone()
        return int(result[0])

    # get range of timestamps for table with name symbol
    def get_table_ts_range(self, symbol):
        table_name = self.get_table_from_symbol(symbol)
        start_ts = self.get_table_start_ts(table_name)
        end_ts = self.get_table_end_ts(table_name)
        return start_ts, end_ts

    # select individual field from symbol table with start_ts <= ts <= end_ts
    def build_sql_select_field_query(self, symbol, field, start_ts, end_ts):
        table_name = self.get_table_from_symbol(symbol)
        sql = "SELECT {} FROM {} ".format(field, table_name)

        if start_ts and end_ts:
            sql += "WHERE ts >= {} AND ts <= {} ".format(start_ts, end_ts)
        elif not start_ts and end_ts:
            sql += "WHERE ts <= {} ".format(end_ts)
        elif start_ts and not end_ts:
            sql += "WHERE {} <= ts ".format(start_ts)

        sql += "ORDER BY ts ASC"
        return sql

    def build_sql_select_query(self, symbol, start_ts, end_ts, daily=False, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        if not columns:
            columns = self.cnames
        elif isinstance(columns, list):
            columns = ','.join(columns)
        sql = "SELECT {} FROM {} ".format(columns, table_name)

        if start_ts and end_ts:
            sql += "WHERE ts >= {} AND ts <= {} ".format(start_ts, end_ts)
        elif not start_ts and end_ts:
            sql += "WHERE ts <= {} ".format(end_ts)
        elif start_ts and not end_ts:
            sql += "WHERE {} <= ts ".format(start_ts)

        if daily:
            if 'WHERE' in sql:
                sql += "AND (ROWID - 1) % 24 = 0 "
            else:
                sql += "WHERE (ROWID - 1) % 24 = 0 "

        sql += "ORDER BY ts ASC"
        return sql

    # get minimum value of a table field from db table
    def get_min_field_value(self, symbol, field, start_ts=0, end_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        sql = "SELECT MIN({}) FROM {}".format(field, table_name)
        if start_ts and end_ts:
            sql += " WHERE ts >= {} AND ts <= {} ".format(start_ts, end_ts)
        elif not start_ts and end_ts:
            sql += " WHERE ts <= {} ".format(end_ts)
        elif start_ts and not end_ts:
            sql += " WHERE {} <= ts ".format(start_ts)
        cur = self.conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        if result:
            return result[0]
        return 0

    # get maximum value of a table field from db table
    def get_max_field_value(self, symbol, field, start_ts=0, end_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        sql = "SELECT MAX({}) FROM {}".format(field, table_name)
        if start_ts and end_ts:
            sql += " WHERE ts >= {} AND ts <= {} ".format(start_ts, end_ts)
        elif not start_ts and end_ts:
            sql += " WHERE ts <= {} ".format(end_ts)
        elif start_ts and not end_ts:
            sql += " WHERE {} <= ts ".format(start_ts)
        cur = self.conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        if result:
            return result[0]
        return 0

    # get klines as list of rows from db table
    def get_raw_klines(self, symbol, start_ts=0, end_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {} ORDER BY ts ASC".format(self.cnames, table_name))
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
            result.append(row)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # get klines as list of dicts from db table
    def get_dict_klines(self, symbol, start_ts=0, end_ts=0, daily=False):
        table_name = self.get_table_from_symbol(symbol)
        result = []
        cur = self.conn.cursor()

        sql = self.build_sql_select_query(table_name, start_ts, end_ts, daily=daily)

        cur.execute(sql)
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
            msg = {}
            for i in range(0, len(self.cnames_list)):
                msg[self.cnames_list[i]] = row[i]
            result.append(msg)
            if end_ts and row[0] >= end_ts:
                break
        return result

    # load single hourly kline in dict format
    def get_dict_kline(self, symbol, hourly_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        sql = "SELECT {} FROM {} WHERE ts = {}".format(self.cnames, table_name, self.accnt.format_ts(hourly_ts))
        cur = self.conn.cursor()
        cur.execute(sql)
        k = cur.fetchone()

        #if kline is not in db yet
        if not k:
            self.logger.warn("{}: '{}' FAILED".format(self.get_dict_kline.__name__, sql))
            return None

        result = {}
        for i in range(0, len(self.cnames_list)):
            result[self.cnames_list[i]] = k[i]
        return result

    # load daily klines in pandas dataframe
    def get_pandas_daily_klines(self, symbol, start_ts=0, end_ts=0, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        sql = self.build_sql_select_query(table_name, start_ts, end_ts, daily=True, columns=columns)
        result = pd.read_sql_query(sql, self.conn)
        return result

    # load hourly klines in pandas dataframe
    def get_pandas_klines(self, symbol, start_ts=0, end_ts=0, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        sql = self.build_sql_select_query(table_name, start_ts, end_ts, columns=columns)
        result = pd.read_sql_query(sql, self.conn)
        return result

    # use pandas dataframe, then get numpy values from dataframe
    def get_numpy_klines(self, symbol, start_ts=0, end_ts=0, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        return self.get_pandas_klines(table_name, start_ts, end_ts, columns).values

    # load single hourly kline in pandas dataframe
    def get_pandas_kline(self, symbol, hourly_ts=0, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        if not columns:
            columns = self.cnames
        elif isinstance(columns, list):
            columns = ','.join(columns)
        sql = "SELECT {} FROM {} WHERE ts = {}".format(columns, table_name, hourly_ts)
        result = pd.read_sql_query(sql, self.conn)
        return result

    # use pandas dataframe, then get numpy values from dataframe
    def get_numpy_kline(self, symbol, hourly_ts=0, columns=None):
        table_name = self.get_table_from_symbol(symbol)
        return self.get_pandas_kline(table_name, hourly_ts, columns).values

    # get klines as list of Kline class from db table
    def get_klines(self, symbol, start_ts=0, end_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT {} from {} ORDER BY ts ASC".format(self.cnames, table_name))
        for row in cur:
            if start_ts and row[0] < start_ts:
                continue
            kline = Kline()
            kline.ts = row[0]
            kline.open = row[1]
            kline.high = row[2]
            kline.low = row[3]
            kline.close = row[4]
            kline.volume = row[5]
            result.append(kline)
            if end_ts and row[0] >= end_ts:
                break
        return result

    def get_kline(self, symbol, hourly_ts=0):
        table_name = self.get_table_from_symbol(symbol)
        sql = "SELECT {} FROM {} WHERE ts = {}".format(self.cnames, table_name, hourly_ts)
        cur = self.conn.cursor()
        cur.execute(sql)
        k = cur.fetchone()

        #if kline is not in db yet
        if not k:
            return None

        kline = Kline()
        kline.ts = k[0]
        kline.open = k[1]
        kline.high = k[2]
        kline.low = k[3]
        kline.close = k[4]
        kline.volume = k[5]
        return kline
