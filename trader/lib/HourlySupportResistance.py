# use hourly klines from hourly klines DB to analyze support/resistance lines
from trader.HourlyKlinesDB import HourlyKlinesDB

class HourlySupportResistance(object):
    def __init__(self, symbol, accnt=None, filename=None, db=None):
        self.accnt = accnt
        self.filename = filename
        self.symbol = symbol
        self.db = db
        if not self.db:
            self.db = HourlyKlinesDB(self.accnt, self.filename, self.symbol)

    def load(self, hourly_start_ts, hourly_end_ts):
        pass

    def update(self, hourly_ts):
        pass

    def process(self):
        pass
