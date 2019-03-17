from trader.indicator.TSI import TSI
from trader.lib.Crossover import Crossover
from trader.signal.SignalBase import SignalBase

class TSI_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, window=26):
        super(TSI_Signal, self).__init__(accnt, symbol, asset_info)
        self.signal_name = "TSI_Signal"
        self.window = window
        #self.obv = OBV()
        self.tsi = TSI()
        #self.obv_ema26 = EMA(self.window, scale=24)
        #self.rsi_ema26 = EMA(self.window, scale=24)
        self.tsi_cross_low = Crossover(window=10)
        self.tsi_cross_zero = Crossover(window=10)
        self.tsi_cross_high = Crossover(window=10)

    def pre_update(self, close, volume, ts, cache_db=None):
        #obv_value = self.obv.update(close=float(close), volume=float(volume))
        tsi_result = self.tsi.update(float(close))

        if tsi_result:
            #self.obv_ema26.update(obv_value)
            #self.rsi_ema26.update(rsi_result)
            self.tsi_cross_low.update(tsi_result, -25)
            self.tsi_cross_high.update(tsi_result, 25)
            self.tsi_cross_zero.update(tsi_result, 0)
            #self.peak.update(tsi_result)

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

        #if self.tsi.result >= 25 and self.peak.peak():
        #    return True

        return False
