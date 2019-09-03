import numpy as np
import pandas as pd


class HourlyMapMovement(object):
    def __init__(self, symbol=None, accnt=None, hkdb=None, win_hours=24):
        self.symbol = symbol
        self.accnt = accnt
        self.hkdb = hkdb
        self.win_hours = win_hours
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self.klines = None
        self.deltas = None
        self.unit_deltas = None
        self.sums = []
        self.unit_sums = []
        self.klines_loaded = False
        self.columns = ['open', 'high', 'low', 'close']

    def ready(self):
        return self.klines_loaded

    def hourly_load(self, hourly_ts=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.win_hours)
        klines = self.hkdb.get_pandas_klines(self.symbol, start_ts=start_ts, end_ts=end_ts, columns=self.columns)
        if len(klines) < self.win_hours + 1:
            return

        #self.kline_deltas = klines.iloc[1:, :].reset_index().iloc[:, 2:6] - klines.iloc[:-1, 1:5]
        #print(self.unit_deltas)
        #print(self.sums)
        #print(self.unit_sums)
        #print(klines.iloc[1:, :].reset_index().iloc[:, 2:6])
        #print(klines.iloc[:-1, 1:5])
        self.klines = klines #pd.DataFrame(klines, columns=['open', 'high', 'low', 'close'])
        self.recompute()
        self.klines_loaded = True
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.win_hours)
        self.klines = self.hkdb.get_pandas_klines(self.symbol, start_ts=start_ts, end_ts=end_ts, columns=self.columns)
        if len(self.klines) < self.win_hours + 1:
            return
        self.recompute()

    def recompute(self):
        self.sums = []
        self.unit_sums = []
        self.deltas = self.klines.shift(-1).dropna().values - self.klines.shift(1).dropna().values
        for delta in self.deltas:
            self.sums.append(np.sum(delta))
        self.unit_deltas = np.where(self.deltas > 0, 1, self.deltas)
        self.unit_deltas = np.where(self.unit_deltas < 0, -1, self.unit_deltas)
        for delta in self.unit_deltas:
            self.unit_sums.append(np.sum(delta))
