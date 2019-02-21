from trader.indicator.EMA import EMA
from trader.indicator.KST import KST
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.signal.SignalBase import SignalBase

class KST_Crossover(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, win_short=12, win_med=26, win_long=50):
        super(KST_Crossover, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "KST_Crossover"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.obv = OBV()
        self.ema12 = EMA(self.win_short, scale=24)
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.kst = KST()
        self.kst_cross = Crossover2(window=10)
        self.kst_cross_zero = Crossover2(window=10)

        #self.box = BOX()
        self.trend_down_count = 0
        self.trend_up_count = 0
        self.trending_up = False
        self.trending_down = False
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.min_price = 0
        self.max_price = 0
        self.ts = 0

    def pre_update(self, close, volume, ts, cache_db=None):
        if self.min_price == 0 or close < self.min_price:
            self.min_price = close

        if self.max_price == 0 or close > self.max_price:
            self.max_price = close

        self.ts = ts

        obv_value = self.obv.update(close=close, volume=volume)
        self.prev_low = self.low
        self.prev_high = self.high

        self.ema12.update(close)
        obv_value1 = self.obv_ema12.update(obv_value)
        obv_value2 = self.obv_ema26.update(obv_value)
        obv_value3 = self.obv_ema50.update(obv_value)

        self.kst.update(close)
        self.kst_cross.update(self.kst.result, self.kst.signal_result)
        self.kst_cross_zero.update(self.kst.result, 0)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result <= self.obv_ema26.last_result:
            return False

        if self.obv_ema12.result <= self.obv_ema12.last_result:
            return False

        #if self.kst.result < 0.0:
        #    return False

        if self.kst_cross.crossup_detected() and self.obv_ema26.result > self.obv_ema26.last_result and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        return False

    def sell_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        #if self.kst.result > 0.0:
        #    return False

        if self.kst_cross.crossdown_detected():
            return True

        return False
