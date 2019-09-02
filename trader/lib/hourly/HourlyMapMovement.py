class HourlyMapMovement(object):
    def __init__(self, symbol=None, accnt=None, hkdb=None, win_hours=24):
        self.symbol = symbol
        self.accnt = accnt
        self.hkdb = hkdb
        self.win_hours = win_hours
        self.first_hourly_ts = 0
        self.last_hourly_ts = 0
        self.last_update_ts = 0
        self.klines = []
        self.klines_loaded = False

    def ready(self):
        return self.klines_loaded

    def hourly_load(self, hourly_ts=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(self.win_hours)
        klines = self.hkdb.get_pandas_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        print(klines)
        if len(klines) < self.win_hours:
            return
        self.klines = klines
        self.klines_loaded = True
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
        pass
