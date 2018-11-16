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
        self.ema_cross_10_30 = MACross(ema_win1=10, ema_win2=30, scale=24) #, indicator=ZLEMA)
        self.ema_cross_30_50 = MACross(ema_win1=30, ema_win2=50, scale=24) #, indicator=ZLEMA)
        self.ema_cross_50_100 = MACross(ema_win1=50, ema_win2=100, scale=24) #, indicator=ZLEMA)
        self.ema_cross_100_200 = MACross(ema_win1=100, ema_win2=200, scale=24)

        self.cross_long = Crossover2(window=10, cutoff=0.0)
        self.obv_cross = Crossover2(window=10, cutoff=0.0)
        self.trend_down_count = 0
        self.trend_up_count = 0
        self.trending_up = False
        self.trending_down = False
        self.obv_trending_up = False
        self.obv_trending_down = False

    def pre_update(self, close, volume, ts):
        if self.timestamp == 0:
            self.timestamp = ts

        self.dtwma_close.update(close, ts)
        self.dtwma_volume.update(volume, ts)

        if not self.dtwma_close.ready() or not self.dtwma_volume.ready():
            return

        dtwma_close = self.dtwma_close.result
        dtwma_volume = self.dtwma_volume.result

        self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(self.obv.result)
        self.obv_ema26.update(self.obv.result)
        self.obv_ema50.update(self.obv.result)

        self.ema_cross_10_30.update(close, ts)
        self.ema_cross_30_50.update(close, ts)
        self.ema_cross_50_100.update(close, ts)
        self.ema_cross_100_200.update(close, ts)

        self.ema100.update(close)
        self.tpv.update(self.ema100.result, ts)
        self.detector.update(self.ema_cross_30_50.get_ma2_result())

        self.ema12.update(close)
        self.ema26.update(close)
        self.ema50.update(close)
        self.ema200.update(close)
        self.cross_long.update(self.ema50.result, self.ema200.result)

        if self.cross_long.crossup_detected():
            self.trending_up = True
            self.trending_down = False
            self.last_cross_ts = ts
        elif self.cross_long.crossdown_detected():
            self.trending_down = True
            self.trending_up = False
            self.last_cross_ts = ts

        self.obv_cross.update(self.obv_ema26.result, self.obv_ema50.result)

        if self.obv_cross.crossup_detected():
            self.obv_trending_up = True
            self.obv_trending_down = False
            self.last_obv_cross_ts = ts
        elif self.obv_cross.crossdown_detected():
            self.obv_trending_up = False
            self.obv_trending_down = False
            self.last_obv_cross_ts = ts

    def buy_signal(self):
        if self.last_sell_ts != 0 and (self.timestamp - self.last_sell_ts) < 1000 * 800:
            return False

        # it has been over an hour since last crossover, and last crossover was a cross down
        if (self.trending_down and self.last_cross_ts != 0 and (self.timestamp - self.last_cross_ts) > (3600 * 1000)):
            return False

        if (self.obv_trending_down and self.last_obv_cross_ts != 0 and (self.timestamp - self.last_obv_cross_ts) > (3600 * 1000)):
            return False

        if self.obv_ema26.result < self.obv_ema26.last_result and self.ema26.result < self.ema26.last_result:
            return False

        if self.obv_ema12.result < self.obv_ema12.last_result and self.ema12.result < self.ema12.last_result:
            return False

        if self.ema_cross_50_100.cross_up and self.ema_cross_30_50.cross_up:
            return True

        if self.ema_cross_10_30.cross_up and self.ema_cross_30_50.cross_up:
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
        if self.ema_cross_50_100.cross_down or self.ema_cross_30_50.cross_down:
            return True

        if self.ema_cross_10_30.cross_down or self.ema_cross_30_50.cross_down:
            return True

        #if self.detector.peak_detect():
        #    return True

        if self.tpv.peak_detected():
            return True

        return False
