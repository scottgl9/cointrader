from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.lib.Crossover2 import Crossover2
from trader.signal.SigType import SigType
from trader.lib.SimplePeak import SimplePeak
from trader.signal.SignalBase import SignalBase

class RSI_OBV(SignalBase):
    def __init__(self, accnt=None, window=26):
        super(RSI_OBV, self).__init__(accnt)
        self.signal_name = "RSI_OBV"
        self.window = window
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.rsi = RSI(window=30, smoother=EMA(12, scale=24))
        self.rsi2 = RSI(window=30, smoother=EMA(26, scale=24))
        #self.obv_ema26 = EMA(self.window, scale=24)
        #self.rsi_ema26 = EMA(self.window, scale=24)
        self.rsi_cross = Crossover2(window=10)

    def pre_update(self, close, volume, ts):
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.ema12.update(close)
        self.ema26.update(close)

        #obv_value = self.obv.update(close=float(close), volume=float(volume))
        rsi_value1 = self.rsi.update(float(close))
        rsi_value2 = self.rsi2.update(float(close))
        self.rsi_cross.update(rsi_value1, rsi_value2)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.rsi.result == 0 or self.rsi2.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result < self.obv_ema26.last_result and self.ema26.result < self.ema26.last_result:
            return False

        if self.obv_ema12.result < self.obv_ema12.last_result and self.ema12.result < self.ema12.last_result:
            return False

        if self.rsi_cross.crossup_detected():
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.rsi.result == 0 or self.rsi2.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        if self.rsi_cross.crossdown_detected():
            return True

        return False
