from .HourlySignalBase import HourlySignalBase
from trader.indicator.ROC import ROC
from trader.lib.Crossover import Crossover


class Hourly_ROC_Signal(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_ROC_Signal, self).__init__(hkdb, accnt, symbol, asset_info)
        self.name = "Hourly_ROC_Signal"
        self.roc = ROC(window=24, use_sma=True)
        self.roc_cross = Crossover(window=2)
        self.cross_down = False
        self.cross_up = False

    def load(self, start_ts=0, end_ts=0, ts=0):
        self.klines = self.hkdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.roc.update(close)
        self.last_update_ts = ts
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def update(self, ts):
        self.last_ts = ts

        if (ts - self.last_hourly_ts) < self.accnt.seconds_to_ts(3600):
            return True

        hourly_ts = self.accnt.get_hourly_ts(ts)
        if hourly_ts == self.last_hourly_ts:
            return True

        kline = self.hkdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        close = float(kline['close'])
        self.roc.update(close)
        self.roc_cross.update(self.roc.result, 0)

        self.last_hourly_ts = hourly_ts

        return True

    def buy(self):
        # hourly ts hasn't been updated in over 2 hours, so return False for buy
        if (self.last_ts - self.last_hourly_ts) >= self.accnt.hours_to_ts(2):
            return False

        if self.roc_cross.crossdown_detected():
            self.cross_down = True
            self.cross_up = False
        elif self.roc_cross.crossup_detected():
            self.cross_down = False
            self.cross_up = True
        if self.cross_down:
            return False
        if not self.cross_down and self.roc.result <= 0:
            return False
        return True
