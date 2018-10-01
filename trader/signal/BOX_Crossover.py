from trader.indicator.test.BOX import BOX
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.signal.SignalBase import SignalBase

class BOX_Crossover(SignalBase):
    def __init__(self, window=50):
        super(BOX_Crossover, self).__init__()
        self.signal_name = "BOX_Crossover"
        self.window = window
        self.box = BOX()
        self.low = 0.0
        self.high = 0.0
        self.prev_low = 0.0
        self.prev_high = 0.0
        self.close = 0.0
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema50 = EMA(50, scale=24, lag_window=5)
        self.below_box = False
        self.above_box = False

    def pre_update(self, close, volume, ts=0):
        obv_value = self.obv.update(close=close, volume=volume)
        self.close = obv_value
        if self.prev_low != self.low:
            self.prev_low = self.low

        if self.prev_high != self.high:
            self.prev_high = self.high

        self.low, self.high = self.box.update(close=close)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.ema12.update(close)
        self.ema26.update(close)
        self.ema50.update(close)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.prev_low == 0 or self.prev_high == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False


        return False

    def sell_signal(self):
        if self.prev_low == 0 or self.prev_high == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        return False
