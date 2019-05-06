from .HourlySignalBase import HourlySignalBase
from trader.indicator.ROC import ROC

class Hourly_ROC_Signal(HourlySignalBase):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None):
        super(Hourly_ROC_Signal, self).__init__(hkdb, accnt, symbol, asset_info)
        self.name = "Hourly_ROC_Signal"
        self.roc = ROC(window=24, use_sma=True)

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
        hourly_ts = self.accnt.get_hourly_ts(ts)
        if hourly_ts == self.last_hourly_ts:
            return True

        kline = self.hkdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        close = float(kline['close'])
        self.roc.update(close)

        self.last_hourly_ts = hourly_ts

        return True

    def buy(self):
        if self.roc.result < 0: # and self.roc.result <= self.roc.last_result:
            return False

        return True
