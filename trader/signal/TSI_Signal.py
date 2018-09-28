from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.TSI import TSI
from trader.lib.Crossover2 import Crossover2
from trader.lib.SimplePeak import SimplePeak


class TSI_Signal(object):
    def __init__(self, window=26):
        self.signal_name = "TSI_Signal"
        self.id = 0
        self.window = window
        #self.obv = OBV()
        self.tsi = TSI()
        #self.obv_ema26 = EMA(self.window, scale=24)
        #self.rsi_ema26 = EMA(self.window, scale=24)
        self.tsi_cross_low = Crossover2(window=10)
        self.tsi_cross_zero = Crossover2(window=10)
        self.tsi_cross_high = Crossover2(window=10)
        self.peak = SimplePeak()

    def set_id(self, id):
        self.id = id

    def pre_update(self, close, volume, ts):
        #obv_value = self.obv.update(close=float(close), volume=float(volume))
        tsi_result = self.tsi.update(float(close))

        if tsi_result:
            #self.obv_ema26.update(obv_value)
            #self.rsi_ema26.update(rsi_result)
            self.tsi_cross_low.update(tsi_result, -25)
            self.tsi_cross_high.update(tsi_result, 25)
            self.tsi_cross_zero.update(tsi_result, 0)
            self.peak.update(tsi_result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.tsi.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.tsi_cross_low.crossup_detected():
            return True

        if self.tsi_cross_zero.crossup_detected():
            return True

        return False

    def sell_signal(self):
        #if self.obv_ema26.result == 0 or self.obv_ema26.last_result == 0:
        #    return False

        if self.tsi.result == 0: # or self.rsi_ema26.result == 0 or self.rsi_ema26.last_result == 0:
            return False

        if self.tsi_cross_high.crossdown_detected():
            return True

        if self.tsi_cross_zero.crossdown_detected():
            return True

        if self.tsi.result >= 25 and self.peak.peak():
            return True

        return False
