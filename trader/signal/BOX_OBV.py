from trader.indicator.test.BOX import BOX
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV


class BOX_OBV(object):
    def __init__(self, window=50):
        self.window = window
        self.box = BOX()
        self.low = 0.0
        self.high = 0.0
        self.prev_low = 0.0
        self.prev_high = 0.0
        self.close = 0.0
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24, lagging=True)
        self.obv_ema26 = EMA(26, scale=24, lagging=True)
        self.obv_ema50 = EMA(50, scale=24, lagging=True, lag_window=5)

    def pre_update(self, close, volume):
        obv_value = self.obv.update(close=close, volume=volume)
        self.close = obv_value
        if self.prev_low != self.low:
            self.prev_low = self.low

        if self.prev_high != self.high:
            self.prev_high = self.high

        self.low, self.high = self.box.update(close=obv_value)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.prev_low == 0 or self.prev_high == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.low < self.prev_low:
            return False

        if self.low < self.close and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        if self.low < self.close and self.obv_ema26.result > self.obv_ema26.last_result:
            return True
        return False

    def sell_signal(self):
        if self.prev_low == 0 or self.prev_high == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.close > self.low and self.close > self.high:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return True

        if self.obv_ema26.result < self.obv_ema26.last_result:
            return True

        if self.low >= self.close:
            return True

        return False
