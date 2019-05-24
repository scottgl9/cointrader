# use hourly klines from hourly klines DB to analyze support/resistance lines
# hourly klines will be used to generate the following information:
# 1) major and minor support/resistance lines in the daily (24hr) timeframe
# 2) major and minor support/resistance lines in the weekly (168hr) timeframe
# 3)  major and minor support/resistance lines in the monthly (730hr) timeframe
from trader.HourlyKlinesDB import HourlyKlinesDB
from trader.lib.struct.CircularArray import CircularArray


class HourlySupportResistance(object):
    def __init__(self, symbol, accnt=None, filename=None, db=None):
        self.accnt = accnt
        self.filename = filename
        self.symbol = symbol
        self.db = db
        if not self.db:
            self.db = HourlyKlinesDB(self.accnt, self.filename, self.symbol)
        self.win_daily = 24
        self.win_weekly = 168
        self.win_monthly = 730
        self.daily_lows = CircularArray(window=self.win_daily)
        self.daily_highs = CircularArray(window=self.win_daily)
        self.weekly_lows = CircularArray(window=self.win_weekly)
        self.weekly_highs = CircularArray(window=self.win_weekly)
        self.monthly_lows = CircularArray(window=self.win_monthly)
        self.monthly_highs = CircularArray(window=self.win_monthly)
        self.daily_support = 0
        self.daily_resistance = 0
        self.weekly_support = 0
        self.weekly_resistance = 0
        self.monthly_support = 0
        self.monthly_resistance = 0

    def load(self, hourly_start_ts=0, hourly_end_ts=0, klines=None):
        if not klines:
            klines = self.db.get_klines(self.symbol, hourly_start_ts, hourly_end_ts)

        for kline in klines:
            self.daily_lows.add(kline.low)
            self.daily_highs.add(kline.high)
            self.weekly_lows.add(kline.low)
            self.weekly_highs.add(kline.high)
            self.monthly_lows.add(kline.low)
            self.monthly_highs.add(kline.high)

    def update(self, hourly_ts=0, kline=None):
        if not kline:
            kline = self.db.get_kline(self.symbol, hourly_ts)

        self.daily_lows.add(kline.low)
        self.daily_highs.add(kline.high)
        self.weekly_lows.add(kline.low)
        self.weekly_highs.add(kline.high)
        self.monthly_lows.add(kline.low)
        self.monthly_highs.add(kline.high)

        if len(self.daily_lows) < self.win_daily:
            return
        self.daily_support = self.daily_lows.min()
        self.daily_resistance = self.daily_highs.max()

        if len(self.weekly_lows) < self.win_weekly:
            return
        self.weekly_support = self.weekly_lows.min()
        self.weekly_resistance = self.weekly_highs.max()

        if len(self.monthly_lows) < self.win_monthly:
            return
        self.monthly_support = self.monthly_lows.min()
        self.monthly_resistance = self.monthly_highs.max()
