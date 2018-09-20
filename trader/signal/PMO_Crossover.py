from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.PMO import PMO
from trader.indicator.ROC import ROC
from trader.lib.Crossover2 import Crossover2
from trader.lib.CrossoverDouble import CrossoverDouble


class PMO_Crossover(object):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        self.signal_name = "PMO_Crossover"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.obv = OBV()
        self.ema12 = EMA(self.win_short, scale=24)
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.pmo = PMO(scale=24)
        self.pmo_cross = Crossover2(window=10, cutoff=0.0)
        self.pmo_zero_cross = Crossover2(window=10, cutoff=0.0)

    def pre_update(self, close, volume, ts):
        self.pmo.update(close)
        if self.pmo.pmo != 0 and self.pmo.pmo_signal != 0:
            self.pmo_cross.update(self.pmo.pmo, self.pmo.pmo_signal)
            self.pmo_zero_cross.update(self.pmo.pmo, 0)
        #obv_value = self.obv.update(close=close, volume=volume)
        #obv_value1 = self.obv_ema12.update(obv_value)
        #obv_value2 = self.obv_ema26.update(obv_value)
        #obv_value3 = self.obv_ema50.update(obv_value)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.pmo_cross.crossup_detected():
            return True

        #if self.pmo_zero_cross.crossup_detected():
        #    return True

        return False

    def sell_signal(self):
        if self.pmo_cross.crossdown_detected():
            return True

        #if self.pmo_zero_cross.crossdown_detected():
        #    return True

        return False
