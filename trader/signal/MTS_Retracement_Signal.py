try:
    from trader.indicator.native.AEMA import AEMA
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.lib.MovingTimeSegment.MTS_Retracement import MTS_Retracement
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
        self.aema2 = AEMA(50, scale_interval_secs=60)
        self.mts_retrace = MTS_Retracement(win_secs=3600)

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
        self.mts_retrace.update(self.aema1.result, ts)

    def buy_signal(self):
        if self.is_currency_pair:
            return False

        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False

        # don't re-buy less than 30 minutes after a sell
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 3600:
            return False

        if self.mts_retrace.crossup_detected(clear=True):
            return True

        return False

    def sell_long_signal(self):
        #if self.mts_retrace.long_crossdown_detected(clear=True):
        #    return True
        return False

    def sell_signal(self):
        if self.mts_retrace.long_crossdown_detected(clear=True):
            return True

        if self.mts_retrace.crossdown_detected(clear=True):
            return True

        return False
