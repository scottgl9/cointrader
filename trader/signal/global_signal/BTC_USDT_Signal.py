from trader.lib.struct.SignalBase import SignalBase
from trader.lib.TrendState.TrendStateTrack import TrendStateTrack
from trader.lib.TrendState.TrendState import TrendState
from trader.indicator.EMA import EMA


class BTC_USDT_Signal(SignalBase):
    def __init__(self, accnt=None):
        super(BTC_USDT_Signal, self).__init__(accnt)
        self.signal_name = "BTC_USDT_Signal"
        self.global_signal = True
        self.global_filter = "BTCUSDT"
        self.accnt = accnt
        self.tst = TrendStateTrack(smoother=EMA(12, scale=24))
        self.timestamp = 0
        self.disable_buy = False
        self.disable_sell = False
        self.enable_buy = False
        self.enable_sell = False

    def pre_update(self, kline):
        close = kline.close
        volume = kline.volume
        ts = kline.ts

        self.timestamp = ts
        self.tst.update(close=close, ts=ts)
        state = self.tst.get_trend_state()
        if (state == TrendState.STATE_TRENDING_DOWN_SLOW or
            state == TrendState.STATE_TRENDING_DOWN_FAST or
            state == TrendState.STATE_CONT_TREND_DOWN_SLOW or
            state == TrendState.STATE_CONT_TREND_DOWN_FAST):
            self.disable_buy = True
            self.enable_buy = False
        else:
            if self.disable_buy:
                self.disable_buy = False
                self.enable_buy = True
