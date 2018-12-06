from trader.signal.SignalBase import SignalBase
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.SLOPE import SLOPE
from trader.lib.Crossover2 import Crossover2

class Slope_Crossover(SignalBase):
    def __init__(self, accnt=None):
        super(Slope_Crossover, self).__init__(accnt)
        self.signal_name = "Slope_Crossover"
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.obv_slope1 = SLOPE(12, use_timestamps=True)
        self.obv_slope2 = SLOPE(26, use_timestamps=True)

        self.ema12 = EMA(12, scale=24, lag_window=5)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.slope1 = SLOPE(12, use_timestamps=True)
        self.slope2 = SLOPE(26, use_timestamps=True)
        self.slope_cross = Crossover2(window=10)

    def pre_update(self, close, volume, ts):
        self.ema12.update(close)
        self.ema26.update(close)
        self.slope1.update(self.ema12.result, ts)
        self.slope2.update(self.ema26.result, ts)
        self.slope_cross.update(self.slope1.result - self.slope2.result, 0)

        obv_value = self.obv.update(close, volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)
        #if self.obv_ema26.result != 0 and self.obv_ema50.result != 0:
        #    self.obv_slope1.update(self.obv_ema26.result)
        #    self.obv_slope2.update(self.obv_ema50.result)


    def buy_signal(self):
        #if (self.obv_slope1.result - self.obv_slope2.result) < 0:
        #    return False

        if self.slope_cross.crossup_detected():
            return True
        return False

    def sell_signal(self):
        if self.slope_cross.crossdown_detected():
            return True
        return False
