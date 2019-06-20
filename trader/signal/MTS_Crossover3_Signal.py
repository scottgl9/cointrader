from trader.indicator.AEMA import AEMA
from trader.indicator.EMA import EMA

from trader.lib.MovingTimeSegment.MTSCrossover3 import MTSCrossover3
from trader.lib.struct.SignalBase import SignalBase


class MTS_Crossover3_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(MTS_Crossover3_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "MTS_Crossover3_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0

        self.aema1 = AEMA(12, scale_interval_secs=60)
        self.aema2 = AEMA(50, scale_interval_secs=60)
        self.aema3 = AEMA(200, scale_interval_secs=60)
        self.cross = MTSCrossover3(win_secs=60)

    def get_cache_list(self):
        if not self.accnt.simulate:
            return None
        return self.cache.get_cache_list()

    def pre_update(self, close, volume, ts, cache_db=None):
        if self.is_currency_pair:
            return False

        if self.timestamp == 0:
            self.timestamp = ts
            if self.is_currency_pair:
                self.disabled = True
                self.disabled_end_ts = self.timestamp + 1000 * 3600
        else:
            self.last_timestamp = self.timestamp
            self.timestamp = ts

        self.last_close = close
        self.last_volume = volume

        self.aema1.update(close, ts)
        self.aema2.update(close, ts)
        self.aema3.update(close, ts)
        self.cross.update(self.aema1.result, self.aema2.result, self.aema3.result, ts)

    def buy_signal(self):
        if self.is_currency_pair:
            return False

        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        # don't re-buy less than 1 hour after a sell
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < self.accnt.hours_to_ts(2):
            return False

        if self.cross.crossup_detected():
            return True

        return False

    def sell_long_signal(self):
        if self.cross.crossdown_detected():
            return True
        return False

    def sell_signal(self):
        if self.cross.cross12_down_detected(clear=False):
            return True
        return False
