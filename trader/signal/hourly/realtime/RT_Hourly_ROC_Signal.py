from trader.lib.struct.SignalBase import SignalBase
from trader.indicator.ROC import ROC
from trader.indicator.EMA import EMA
from trader.lib.Crossover import Crossover
from trader.lib.Crossover2 import Crossover2
import time


class RT_Hourly_ROC_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(Hourly_ROC_Signal, self).__init__(accnt, symbol, asset_info, kdb, uses_models=False)
        self.name = "RT_Hourly_ROC_Signal"
        self.roc = ROC(window=1,  smoother=EMA(12))
        self.roc_cross = Crossover2(window=10)
        self.cross_down = False
        self.cross_up = False

    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        end_ts = hourly_ts
        start_ts = end_ts - self.accnt.hours_to_ts(pre_load_hours)
        self.klines = self.kdb.get_dict_klines(self.symbol, start_ts=start_ts, end_ts=end_ts)
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.roc.update(close)
        self.last_update_ts = ts
        #if self.accnt.simulate:
        self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        #else:
        #    ts = int(time.time() * 1000)
        #    self.first_hourly_ts = self.accnt.get_hourly_ts(ts)
        self.last_hourly_ts = self.first_hourly_ts

    def hourly_update(self, hourly_ts):
         # wait 1 hour + 2 minutes before doing an update
        #if (ts - self.last_hourly_ts) < self.accnt.seconds_to_ts(3720):
        #    return True

        #hourly_ts = self.accnt.get_hourly_ts(ts)
        #if hourly_ts == self.last_hourly_ts:
        #    return True

        #if not self.accnt.simulate and last_hourly_ts:
        #    # do not get kline from DB until all tables have been updated
        #    if self.last_hourly_ts == last_hourly_ts:
        #        return True

        kline = self.kdb.get_dict_kline(self.symbol, hourly_ts)

        # hourly kline not in db yet, wait until next update() call
        if not kline:
            return False

        close = float(kline['close'])
        self.roc.update(close)
        self.roc_cross.update(self.roc.result, 0, hourly_ts)

        self.last_hourly_ts = hourly_ts

        return True

    def hourly_buy_enable(self):
        # hourly ts hasn't been updated in over 2 hours, so return False for buy
        #if (self.last_ts - self.last_hourly_ts) >= self.accnt.hours_to_ts(2):
        #    return False

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
