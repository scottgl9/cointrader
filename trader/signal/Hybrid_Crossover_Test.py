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

        self.ema10 = ZLEMA(10, scale=24)
        self.ema30 = ZLEMA(30, scale=24, lag_window=5)
        self.ema50 = ZLEMA(50, scale=24, lag_window=5)
        self.ema100 = ZLEMA(100, scale=24, lag_window=5)
        self.detector = PeakValleyDetect()
        self.ema200 = ZLEMA(200, scale=24, lag_window=5)

        self.obv = OBV()
        self.obv_ema12 = ZLEMA(12, scale=24)
        self.obv_ema26 = ZLEMA(26, scale=24, lag_window=5)
        self.obv_ema50 = ZLEMA(50, scale=24, lag_window=5)

        self.ema_cross_1050 = MACross(10, 50, scale=24, indicator=ZLEMA)
        self.ema_cross_3050 = MACross(30, 50, scale=24, indicator=ZLEMA)

        self.cross_ema10_ema50 = Crossover2(window=10, cutoff=0.0)
        self.cross_ema10_ema50_ts = 0
        self.last_cross_ema10_ema50_ts = 0
        self.cross_ema10_ema50_up = False
        self.cross_ema10_ema50_down = False

        self.cross_ema30_ema50 = Crossover2(window=10, cutoff=0.0)
        self.cross_ema30_ema50_ts = 0
        self.last_cross_ema30_ema50_ts = 0
        self.cross_ema30_ema50_up = False
        self.cross_ema30_ema50_down = False

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

        #self.ema10.update(dtwma_close)
        #self.ema30.update(dtwma_close)
        #self.ema50.update(dtwma_close)
        #self.cross_ema10_ema50.update(self.ema10.result, self.ema50.result)
        #self.cross_ema30_ema50.update(self.ema30.result, self.ema50.result)

        self.ema_cross_1050.update(dtwma_close, ts)
        self.ema_cross_3050.update(dtwma_close, ts)

        # if self.cross_ema10_ema50.crossup_detected():
        #     self.cross_ema10_ema50_up = True
        #     self.cross_ema10_ema50_down = False
        #     self.last_cross_ema10_ema50_ts = self.cross_ema10_ema50_ts
        #     self.cross_ema10_ema50_ts = ts
        # elif self.cross_ema10_ema50.crossdown_detected():
        #     self.cross_ema10_ema50_up = False
        #     self.cross_ema10_ema50_down = True
        #     self.last_cross_ema10_ema50_ts = self.cross_ema10_ema50_ts
        #     self.cross_ema10_ema50_ts = ts
        #
        # if self.cross_ema30_ema50.crossup_detected():
        #     self.cross_ema30_ema50_up = True
        #     self.cross_ema30_ema50_down = False
        #     self.last_cross_ema30_ema50_ts = self.cross_ema30_ema50_ts
        #     self.cross_ema30_ema50_ts = ts
        # elif self.cross_ema30_ema50.crossdown_detected():
        #     self.cross_ema30_ema50_up = False
        #     self.cross_ema30_ema50_down = True
        #     self.last_cross_ema30_ema50_ts = self.cross_ema30_ema50_ts
        #     self.cross_ema30_ema50_ts = ts

    def buy_signal(self):
        #if self.obv_ema50.result == 0 or self.obv_ema50.last_result == 0:
        #    return False

        #if self.obv_ema50.result < self.obv_ema50.last_result:
        #    return False

        #if self.cross_ema10_ema50_up and self.cross_ema30_ema50_up:
        if self.ema_cross_1050.cross_up and self.ema_cross_3050.cross_up:
            #if abs(self.cross_ema30_ema50_down - self.last_cross_ema30_ema50_ts) < 1000 * 300:
            #    return False
            #if abs(self.cross_ema10_ema50_down - self.last_cross_ema10_ema50_ts) < 1000 * 300:
            #    return False
            return True

        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        #if self.cross_ema10_ema50_down or self.cross_ema30_ema50_down:
        if self.ema_cross_1050.cross_up or self.ema_cross_3050.cross_up:
            return True

        return False
