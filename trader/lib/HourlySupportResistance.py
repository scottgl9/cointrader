# use hourly klines from hourly klines DB to analyze support/resistance lines
from trader.HourlyKlinesDB import HourlyKlinesDB


class HourlySupportResistance(object):
    def __init__(self, symbol, accnt=None, filename=None, db=None):
        self.accnt = accnt
        self.filename = filename
        self.symbol = symbol
        self.db = db
        self.klines = None
        if not self.db:
            self.db = HourlyKlinesDB(self.accnt, self.filename, self.symbol)

    def load(self, hourly_start_ts=0, hourly_end_ts=0, klines=None):
        if klines:
            self.klines = klines
        else:
            self.klines = self.db.get_klines(self.symbol, hourly_start_ts, hourly_end_ts)

    def update(self, hourly_ts=0, kline=None):
        if not kline:
            kline = self.db.get_kline(self.symbol, hourly_ts)
        if not self.klines:
            self.klines = [kline]
        else:
            self.klines.append(kline)

    def process(self):
        if not self.klines:
            return