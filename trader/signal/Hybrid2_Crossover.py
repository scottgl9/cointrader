# Combination of MACD, OBV
from trader.indicator.MACD import MACD
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.RSI import RSI
from trader.indicator.DTWMA import DTWMA
from trader.lib.Crossover2 import Crossover2
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Hybrid2_Crossover(SignalBase):
    def __init__(self, accnt=None, symbol=None, win_short=12, win_med=26, win_long=50):
        super(Hybrid2_Crossover, self).__init__(accnt, symbol)
        self.signal_name = "Hybrid2_Crossover"
        #self.id = 0
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.obv = OBV()
        self.ema12 = EMA(self.win_short, scale=24)
        self.ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.ema100 = EMA(100, scale=24, lag_window=5)
        self.detector = PeakValleyDetect()
        self.ema200 = EMA(200, scale=24, lag_window=5)
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.macd = MACD(scale=10)
        self.macd_cross = Crossover2(window=10)
        self.macd_zero_cross = Crossover2(window=10)
        self.cross_long = Crossover2(window=10)
        self.obv_cross = Crossover2(window=10)

        # delta timestamp WMA
        self.dtwma = DTWMA(window=30)
        self.dtwma_volume = DTWMA(window=30)

        self.rsi = RSI(window=14)
        self.rsi_cross70 = Crossover2(window=10)
        self.rsi_cross30 = Crossover2(window=10)

        self.trend_down_count = 0
        self.trend_up_count = 0
        self.trending_up = False
        self.trending_down = False
        self.obv_trending_up = False
        self.obv_trending_down = False
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.min_price = 0
        self.max_price = 0
        self.ts = 0
        self.last_cross_ts = 0
        self.last_obv_cross_ts = 0

    def pre_update(self, close, volume, ts, cache_db=None):
        if self.min_price == 0 or close < self.min_price:
            self.min_price = close

        if self.max_price == 0 or close > self.max_price:
            self.max_price = close

        if close == 0 or volume == 0:
            return

        self.dtwma.update(close, ts)
        close = self.dtwma.result
        self.dtwma_volume.update(volume, ts)
        volume = self.dtwma_volume.result

        if close == 0 or volume == 0:
            return

        self.ts = ts

        self.rsi.update(close)
        self.rsi_cross70.update(self.rsi.result, 70)
        self.rsi_cross30.update(self.rsi.result, 30)

        obv_value = self.obv.update(close=close, volume=volume)
        self.prev_low = self.low
        self.prev_high = self.high

        self.ema12.update(close)
        self.ema26.update(close)
        value1 = self.ema50.update(close)
        value2 = self.ema200.update(close)

        self.ema100.update(close)
        self.detector.update(self.ema100.result)

        self.macd.update(close)
        self.macd_cross.update(self.macd.result, self.macd.result_signal)
        self.macd_zero_cross.update(self.macd.result, 0)
        self.cross_long.update(value1, value2)

        if self.cross_long.crossup_detected():
            self.trending_up = True
            self.trending_down = False
            self.last_cross_ts = ts
        elif self.cross_long.crossdown_detected():
            self.trending_down = True
            self.trending_up = False
            self.last_cross_ts = ts

        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.obv_cross.update(self.obv_ema26.result, self.obv_ema50.result)

        if self.obv_cross.crossup_detected():
            self.obv_trending_up = True
            self.obv_trending_down = False
            self.last_obv_cross_ts = ts
        elif self.obv_cross.crossdown_detected():
            self.obv_trending_up = False
            self.obv_trending_down = False
            self.last_obv_cross_ts = ts


    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.macd.result == 0 or self.macd.signal.result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result < self.obv_ema26.last_result and self.ema26.result < self.ema26.last_result:
            return False

        if self.obv_ema12.result < self.obv_ema12.last_result and self.ema12.result < self.ema12.last_result:
            return False

        # it has been over an hour since last crossover, and last crossover was a cross down
        if (self.trending_down and self.last_cross_ts != 0 and (self.ts - self.last_cross_ts) > (3600 * 1000)):
            return False

        if (self.obv_trending_down and self.last_obv_cross_ts != 0 and (self.ts - self.last_obv_cross_ts) > (3600 * 1000)):
            return False

        if self.rsi.result < 25:
            return False

        if self.rsi_cross70.crossup_detected():
            return True

        if self.macd_cross.crossup_detected():
            self.buy_type = SigType.SIGNAL_SHORT
            return True

        if self.macd_zero_cross.crossup_detected():
            self.buy_type = SigType.SIGNAL_SHORT
            return True

        if self.detector.valley_detect():
            return True

        return False

    def sell_long_signal(self):
        if (self.trending_down and self.last_cross_ts != 0 and (self.ts - self.last_cross_ts) > (3600 * 1000 * 4)
            and self.ema200.result <= self.ema200.last_result):
            self.sell_type = SigType.SIGNAL_LONG
            return True
        return False

    def sell_signal(self):
        if self.macd.result == 0 or self.macd.signal.result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        if self.rsi_cross30.crossdown_detected():
            return True

        if self.macd_cross.crossdown_detected():
            self.sell_type = SigType.SIGNAL_SHORT
            return True

        if self.macd_zero_cross.crossdown_detected():
            self.sell_type = SigType.SIGNAL_SHORT
            return True

        if self.detector.peak_detect():
            return True

        return False
