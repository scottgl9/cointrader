try:
    from trader.indicator.native.AEMA import AEMA
    from trader.indicator.native.EMA import EMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
from trader.lib.struct.SignalBase import SignalBase


class MTS_Crossover2_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(MTS_Crossover2_Signal, self).__init__(accnt, symbol, asset_info, kdb)
        self.signal_name = "MTS_Crossover2_Signal"
        self.disabled = False
        self.disabled_end_ts = 0
        self.start_timestamp = 0
        self.last_close = 0
        self.last_volume = 0

        self.aema1 = AEMA(12, scale_interval_secs=60)
        self.aema2 = AEMA(50, scale_interval_secs=60)
        self.cross = MTSCrossover2(win_secs=60)
        self.last_crossup_value = 0
        self.last_crossup_ts = 0
        self.last_crossdown_value = 0
        self.last_crossdown_ts = 0

    def get_cache_list(self):
        if not self.accnt.simulate:
            return None
        return self.cache.get_cache_list()

    def pre_update(self, kline):
        close = kline.close
        volume = kline.volume
        ts = kline.ts

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
        self.cross.update(value1=self.aema1.result, value2=self.aema2.result, ts=ts)

        if self.cross.crossup_detected():
            self.last_crossup_value = self.cross.crossup_value
            self.last_crossup_ts = self.cross.crossup_ts
        elif self.cross.crossdown_detected():
            self.last_crossdown_value = self.cross.crossdown_value
            self.last_crossdown_ts = self.cross.crossdown_ts

    def buy_signal(self):
        if not self.last_crossup_ts:
            return False

        if self.last_crossdown_ts > self.last_crossup_ts:
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

        if self.aema2.result <= self.last_crossup_value:
            return False

        if 100.0 * (self.aema1.result - self.last_crossup_value) / self.last_crossup_value >= 1.0:
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        if not self.last_crossdown_ts:
            return False

        if self.last_crossup_ts > self.last_crossdown_ts:
            return False

        if self.aema2.result <= self.last_crossdown_value:
            return True

        return False
