# Testing code for complete rewrite of Hybrid_Crossover for better profits
from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Crossover2 import Crossover2
from trader.lib.MACross import MACross
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test(SignalBase):
    def __init__(self):
        super(Hybrid_Crossover_Test, self).__init__()
        self.signal_name = "Hybrid_Crossover_Test"
        self.dtwma_close = DTWMA(30)
        self.dtwma_volume = DTWMA(30)

        self.detector = PeakValleyDetect()
        self.obv = OBV()
        self.obv_ema12 = ZLEMA(12, scale=24)
        self.obv_ema26 = ZLEMA(26, scale=24, lag_window=5)
        self.obv_ema50 = ZLEMA(50, scale=24, lag_window=5)

        self.ema_cross_10_30 = MACross(ema_win1=10, ema_win2=30, scale=24) #, indicator=ZLEMA)
        self.ema_cross_30_50 = MACross(ema_win1=30, ema_win2=50, scale=24) #, indicator=ZLEMA)
        self.ema_cross_50_100 = MACross(ema_win1=50, ema_win2=100, scale=24) #, indicator=ZLEMA)
        self.ema_cross_100_200 = MACross(ema_win1=100, ema_win2=200, scale=24)

    def pre_update(self, close, volume, ts):
        self.dtwma_close.update(close, ts)
        self.dtwma_volume.update(volume, ts)

        if not self.dtwma_close.ready() or not self.dtwma_volume.ready():
            return

        dtwma_close = self.dtwma_close.result
        dtwma_volume = self.dtwma_volume.result

        self.obv.update(close=dtwma_close, volume=dtwma_volume)
        self.obv_ema12.update(self.obv.result)
        self.obv_ema26.update(self.obv.result)
        self.obv_ema50.update(self.obv.result)

        self.ema_cross_10_30.update(close, ts)
        self.ema_cross_30_50.update(close, ts)
        self.ema_cross_50_100.update(close, ts)
        self.ema_cross_100_200.update(close, ts)

        self.detector.update(self.ema_cross_30_50.get_ma2_result())

    def buy_signal(self):
        if self.ema_cross_50_100.cross_up:
            return True

        if self.ema_cross_10_30.cross_up and self.ema_cross_30_50.cross_up:
            return True

        if self.detector.valley_detect():
            return True

        return False

    def sell_long_signal(self):
        #if self.ema_cross_100_200.cross_down:
        #    return True
        return False

    def sell_signal(self):
        #if self.ema_cross_50_100.cross_down:
        #    return True

        if self.ema_cross_10_30.cross_down or self.ema_cross_30_50.cross_down:
            return True

        if self.detector.peak_detect():
            return True

        return False
