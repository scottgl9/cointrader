# Testing code for complete rewrite of Hybrid_Crossover for better profits
try:
    from trader.indicator.native.EMA import EMA
    from trader.indicator.native.AEMA import AEMA
except ImportError:
    from trader.indicator.AEMA import AEMA
    from trader.indicator.EMA import EMA

from trader.lib.MACross import MACross
from trader.lib.struct.SignalBase import SignalBase
from trader.lib.TrendState.TrendStateTrack import TrendStateTrack


class AEMA_Crossover_Test(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(AEMA_Crossover_Test, self).__init__(accnt, symbol, asset_info, kdb)
        self.signal_name = "AEMA_Crossover_Test"
        self.disabled = False
        self.disabled_end_ts = 0

        self.aema12 = AEMA(12, scale_interval_secs=60, lag_window=3)
        self.aema50 = AEMA(50, scale_interval_secs=60, lag_window=3)
        self.aema100 = AEMA(100, scale_interval_secs=60, lag_window=3)
        self.aema200 = AEMA(200, scale_interval_secs=60, lag_window=3)

        self.tst = TrendStateTrack()

        ctimeout = 1000 * 3600
        self.aema_cross_12_50 = MACross(cross_timeout=ctimeout)
        self.aema_cross_12_100 = MACross(cross_timeout=ctimeout)
        self.aema_cross_12_200 = MACross(cross_timeout=ctimeout)
        self.aema_cross_50_200 = MACross(cross_timeout=ctimeout)

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

        self.aema12.update(close, ts)
        self.aema50.update(close, ts)
        self.aema100.update(close, ts)
        self.aema200.update(close, ts)

        self.aema_cross_12_50.update(close, ts, ma1_result=self.aema12.result, ma2_result=self.aema50.result)
        self.aema_cross_12_100.update(close, ts, ma1_result=self.aema12.result, ma2_result=self.aema100.result)
        self.aema_cross_12_200.update(close, ts, ma1_result=self.aema12.result, ma2_result=self.aema200.result)
        self.aema_cross_50_200.update(close, ts, ma1_result=self.aema50.result, ma2_result=self.aema200.result)

        self.tst.update(self.aema12.result, ts=ts)

    def buy_signal(self):
        if self.disabled:
            if self.timestamp > self.disabled_end_ts:
                self.disabled = False
                self.disabled_end_ts = 0
            else:
                return False
        if self.aema_cross_12_50.cross_up and self.aema_cross_12_50.ma2_trend_up():
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        if self.aema_cross_12_50.cross_down:
            return True
        return False
