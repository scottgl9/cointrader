from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI


class RSI_OBV(object):
    def __init__(self, window=26):
        self.window = window
        self.obv = OBV()
        self.rsi = RSI()
        self.obv_ema26 = EMA(self.window, scale=24, lagging=True)
        self.rsi_ema26 = EMA(self.window, scale=24, lagging=True)

    def pre_update(self, close, volume):
        obv_value = self.obv.update(close=float(close), volume=float(volume))
        rsi_result = self.rsi.update(float(close))

        if rsi_result:
            self.obv_ema26.update(obv_value)
            self.rsi_ema26.update(rsi_result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.rsi.result == 0 or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.rsi.result > 50.0:
            return False

        if self.rsi_ema26.result > self.rsi_ema26.last_result and self.obv_ema26.result > self.obv_ema26.last_result:
            return True

        return False

    def sell_signal(self):
        if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.rsi.result == 0 or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.rsi.result < 50.0:
            return False

        if self.rsi_ema26.result < self.rsi_ema26.last_result:
            return True

        if self.obv_ema26.result < self.obv_ema26.last_result:
            return True

        return False
