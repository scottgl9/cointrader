try:
    from trader.indicator.native.AEMA import AEMA
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.indicator.OBV import OBV
from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.MovingTimeSegment.MTS_SMA import MTS_SMA
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.struct.SignalBase import SignalBase


class MTS_SMA_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(MTS_SMA_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "MTS_SMA_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0
        self.mts1 = MTS_SMA(seconds=3600)
        self.mts2 = MovingTimeSegment(seconds=3600)
        self.mts3 = MovingTimeSegment(seconds=3600)
        self.cross = MTSCrossover2(win_secs=60)
        self.cross_long = MTSCrossover2(win_secs=60)

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

        self.mts1.update(close, ts)
        if not self.mts1.ready():
            return False
        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return False
        self.cross.update(self.mts1.last_value(), self.mts2.first_value(), ts)

        self.mts3.update(self.mts2.first_value(), ts)
        if not self.mts3.ready():
            return False
        self.cross_long.update(self.mts1.last_value(), self.mts3.first_value(), ts)

    def buy_signal(self):
        if self.is_currency_pair:
            return False

        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        if self.cross.crossup_detected():
            return True

        return False

    def sell_long_signal(self):
        if not self.mts3.ready():
            return False
        if self.mts1.diff() >= 0 or self.mts2.diff() >= 0 or self.mts3.diff() >= 0:
            return False
        if self.mts1.min() >= self.mts2.min() or self.mts1.min() >= self.mts3.min():
            return False
        if self.mts1.max() < self.mts3.min() and self.cross_long.crossdown_detected():
            self.disabled = True
            self.disabled_end_ts = self.timestamp + 8000 * 3600
            return True
        return False

    def sell_signal(self):
        if self.cross.crossdown_detected():
            return True
        return False
