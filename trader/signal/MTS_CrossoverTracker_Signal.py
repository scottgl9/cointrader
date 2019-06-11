from trader.indicator.AEMA import AEMA
from trader.indicator.EMA import EMA

from trader.lib.CrossoverTracker import CrossoverTracker
from trader.lib.struct.SignalBase import SignalBase


class MTS_CrossoverTracker_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(MTS_CrossoverTracker_Signal, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "MTS_CrossoverTracker_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0

        self.aema1 = AEMA(12, scale_interval_secs=60)
        self.aema2 = AEMA(100, scale_interval_secs=60)
        self.cross_tracker = CrossoverTracker(win_secs=60, hourly_mode=False)

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
        self.cross_tracker.update(value1=self.aema1.result, value2=self.aema2.result, ts=ts)

    def buy_signal(self):
        if self.is_currency_pair:
            return False

        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        if self.cross_tracker.cross_up_detected():
            return True

        return False

    def sell_long_signal(self):
        if self.cross_tracker.cross_down_detected():
            return True
        return False

    def sell_signal(self):
        if self.cross_tracker.cross_down_detected():
            return True
        return False
