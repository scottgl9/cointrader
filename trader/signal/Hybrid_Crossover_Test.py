from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Crossover2 import Crossover2
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test(SignalBase):
    def __init__(self):
        super(Hybrid_Crossover_Test, self).__init__()
        self.signal_name = "Hybrid_Crossover_Test"
        self.obv = OBV()
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema50 = EMA(50, scale=24, lag_window=5)
        self.ema100 = EMA(100, scale=24, lag_window=5)
        self.detector = PeakValleyDetect()
        self.ema200 = EMA(200, scale=24, lag_window=5)
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.macd = MACD(scale=24)
        self.macd_cross = Crossover2(window=10, cutoff=0.0)
        self.macd_zero_cross = Crossover2(window=10, cutoff=0.0)
        self.cross_long = Crossover2(window=10, cutoff=0.0)
        self.obv_cross = Crossover2(window=10, cutoff=0.0)

    def pre_update(self, close, volume, ts):
        pass

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        return False
