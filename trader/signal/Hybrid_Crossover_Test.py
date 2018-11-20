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
from trader.lib.TimePeakValley import TimePeakValley
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid_Crossover_Test(SignalBase):
    def __init__(self):
        super(Hybrid_Crossover_Test, self).__init__()
        self.signal_name = "Hybrid_Crossover_Test"
        self.dtwma_close = DTWMA(30)
        self.dtwma_volume = DTWMA(30)

        self.tpv = TimePeakValley(reverse_secs=600, span_secs=3600)
        self.detector = PeakValleyDetect()
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema100 = ZLEMA(100, scale=24)
        self.ema50 = EMA(50, scale=24, lag_window=5)
        self.ema200 = EMA(200, scale=24, lag_window=5)

        cross_timeout = 1000 * 300
        self.ema_cross_12_26 = MACross(ema_win1=12, ema_win2=26, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_26_50 = MACross(ema_win1=26, ema_win2=50, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_50_100 = MACross(ema_win1=50, ema_win2=100, scale=24, cross_timeout=cross_timeout)
        self.ema_cross_100_200 = MACross(ema_win1=100, ema_win2=200, scale=24, cross_timeout=cross_timeout)

        self.obv_ema_cross_12_26 = MACross(ema_win1=12, ema_win2=26, scale=24) #, cross_timeout=cross_timeout)

    def pre_update(self, close, volume, ts):
        if self.timestamp == 0:
            self.timestamp = ts

        #self.dtwma_close.update(close, ts)
        #self.dtwma_volume.update(volume, ts)

        #if not self.dtwma_close.ready() or not self.dtwma_volume.ready():
        #   return

        #dtwma_close = self.dtwma_close.result
        #dtwma_volume = self.dtwma_volume.result

        self.obv.update(close=close, volume=volume)
        self.obv_ema_cross_12_26.update(self.obv.result, ts)

        self.ema_cross_12_26.update(close, ts)
        self.ema_cross_26_50.update(close, ts)
        self.ema_cross_50_100.update(close, ts)
        self.ema_cross_100_200.update(close, ts)

        self.ema100.update(close)
        self.tpv.update(self.ema100.result, ts)
        self.detector.update(self.ema_cross_26_50.get_ma2_result())

        self.ema12.update(close)
        self.ema26.update(close)
        self.ema50.update(close)
        self.ema200.update(close)
        #self.cross_long.update(self.ema50.result, self.ema200.result)

    def buy_signal(self):
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 800:
            return False

        # it has been over an hour since last crossover, and last crossover was a cross down
        #if (self.trending_down and self.last_cross_ts != 0 and (self.timestamp - self.last_cross_ts) > (3600 * 1000)):
        #    return False

        #if (self.obv_trending_down and self.last_obv_cross_ts != 0 and (self.timestamp - self.last_obv_cross_ts) > (3600 * 1000)):
        #    return False

        #if self.obv_ema26.result < self.obv_ema26.last_result and self.ema26.result < self.ema26.last_result:
        #    return False

        #if self.obv_ema12.result < self.obv_ema12.last_result and self.ema12.result < self.ema12.last_result:
        #    return False

        #if not self.obv_ema_cross_12_26.cross_up:
        #    return False

        if self.ema_cross_50_100.cross_up and self.ema_cross_26_50.cross_up:
            return True

        if self.ema_cross_12_26.cross_up and self.ema_cross_26_50.cross_up:
            return True

        #if self.detector.valley_detect():
        #    return True
        if self.tpv.valley_detected():
            return True

        return False

    def sell_long_signal(self):
        if self.buy_price == 0 or self.last_buy_ts == 0:
            return False
        if (self.timestamp - self.last_buy_ts) > 3600 * 1000:
            if (self.buy_price_high - self.buy_price) / self.buy_price <= 0.005:
                return True
        return False

    def sell_signal(self):
        if self.ema_cross_50_100.cross_down:
            return True

        if self.ema_cross_26_50.cross_down:
            return True

        if self.ema_cross_12_26.cross_down:
            return True

        #if self.detector.peak_detect():
        #    return True

        if self.tpv.peak_detected():
            return True

        return False
