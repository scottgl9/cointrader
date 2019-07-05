try:
    from trader.indicator.native.AEMA import AEMA
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.indicator.OBV import OBV
from trader.lib.MovingTimeSegment.MTS_Retracement import MTS_Retracement
from trader.lib.MovingTimeSegment.MTS_LSMA import MTS_LSMA
from trader.lib.MovingTimeSegment.MTSCrossover import MTSCrossover
from trader.lib.struct.SignalBase import SignalBase


class MTS_Retracement_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(MTS_Retracement_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "MTS_Retracement_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0

        self.aema1 = AEMA(12, scale_interval_secs=60)
        self.aema2 = AEMA(200, scale_interval_secs=60)
        self.mts_retrace = MTS_Retracement(win_secs=3600,
                                           short_smoother=self.aema1,
                                           symbol=self.symbol,
                                           accnt=self.accnt,
                                           hkdb=self.hkdb)

    def get_cache_list(self):
        if not self.accnt.simulate:
            return None
        return self.cache.get_cache_list()

    def hourly_load(self, start_ts=0, end_ts=0, ts=0):
        self.mts_retrace.hourly_load(start_ts, end_ts, ts)

    def hourly_update(self, hourly_ts):
        self.mts_retrace.hourly_update(hourly_ts)

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

        self.mts_retrace.update(close, ts)

    def buy_signal(self):
        if self.is_currency_pair:
            return False

        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        if self.mts_retrace.crossup_detected(clear=True):
            return True

        return False

    def sell_long_signal(self):
        #if self.mts_retrace.long_crossdown_detected(clear=True):
        #    return True
        return False

    def sell_signal(self):
        if self.mts_retrace.crossdown2_detected(clear=True):
            return True

        if self.mts_retrace.crossdown_detected(clear=True):
            return True

        return False
