from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.lib.Crossover2 import Crossover2
from trader.lib.SimplePeak import SimplePeak

class RSI_OBV(object):
    def __init__(self, window=26):
        self.window = window
        #self.obv = OBV()
        self.rsi = RSI()
        #self.obv_ema26 = EMA(self.window, scale=24)
        #self.rsi_ema26 = EMA(self.window, scale=24)
        self.max_rsi = 0
        self.rsi_cross_low = Crossover2(window=10)
        self.rsi_cross_high = Crossover2(window=10)
        self.peak = SimplePeak()

    def pre_update(self, close, volume, ts):
        #obv_value = self.obv.update(close=float(close), volume=float(volume))
        rsi_result = self.rsi.update(float(close))

        if rsi_result:
            if rsi_result > self.max_rsi: self.max_rsi = rsi_result
            #self.obv_ema26.update(obv_value)
            #self.rsi_ema26.update(rsi_result)
            self.rsi_cross_low.update(rsi_result, 30)
            self.rsi_cross_high.update(rsi_result, 70)
            self.peak.update(rsi_result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.rsi.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.rsi_cross_low.crossup_detected():
            return True

        return False

    def sell_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.rsi.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.rsi_cross_high.crossdown_detected():
            return True

        if self.rsi.result >= 70 and self.peak.peak():
            return True

        return False
