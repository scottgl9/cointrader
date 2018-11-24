from trader.indicator.EMA import EMA
from trader.indicator.KST import KST
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.lib.CrossoverDouble import CrossoverDouble
from trader.signal.SignalBase import SignalBase

class EMA_OBV_Crossover(SignalBase):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        super(EMA_OBV_Crossover, self).__init__()
        self.signal_name = "EMA_OBV_Crossover"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.ema12 = EMA(self.win_short, scale=24)
        self.ema26 = EMA(self.win_med, scale=24)
        self.ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.cross_short = Crossover2(window=10)
        self.cross_long = Crossover2(window=10)
        self.cross_double = CrossoverDouble(window=10)
        self.kst = KST()
        self.obv = OBV()
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)

        self.trend_down_count = 0
        self.trend_up_count = 0
        self.trending_up = False
        self.trending_down = False
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.min_price = 0
        self.max_price = 0

    def pre_update(self, close, volume, ts):
        if self.min_price == 0 or close < self.min_price:
            self.min_price = close

        if self.max_price == 0 or close > self.max_price:
            self.max_price = close

        obv_value = self.obv.update(close=close, volume=volume)
        self.prev_low = self.low
        self.prev_high = self.high
        #self.low, self.high = self.box.update(close=obv_value)

        #if (self.low < self.prev_low and self.high <= self.prev_high or
        #    self.low <= self.prev_low and self.high < self.prev_high):
        #    self.trending_up = False
        #    self.trending_down = True
        #    self.trend_down_count += 1

        #if (self.low > self.prev_low and self.high >= self.prev_high or
        #    self.low >= self.prev_low and self.high > self.prev_high):
        #    self.trending_up = True
        #    self.trending_down = False
        #    self.trend_up_count += 1

        #self.testma.update(close)

        obv_value1 = self.obv_ema12.update(obv_value)
        obv_value2 = self.obv_ema26.update(obv_value)
        obv_value3 = self.obv_ema50.update(obv_value)

        self.kst.update(close)

        value1 = self.ema12.update(close)
        value2 = self.ema26.update(close)
        value3 = self.ema50.update(close)
        #self.roc_ema26.update(price=value1, ts=ts)
        #self.roc_ema50.update(price=value2, ts=ts)

        #self.cross_short.update(value1, value2)
        #self.cross_long.update(value2, value3)
        self.cross_short.update(value1, value2)
        self.cross_long.update(value2, value3)
        self.cross_double.update(value1, value2, value3)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.ema50.last_result == 0 or self.ema12.last_result == 0 or self.ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.min_price == 0 or self.max_price == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
           return False

        if self.obv_ema26.result <= self.obv_ema26.last_result:
            return False

        if self.obv_ema12.result <= self.obv_ema12.last_result:
            return False

        if (self.max_price - self.min_price) / self.min_price <= 0.01:
            return False

        #if self.kst.result < 0.0:
        #    return False

        #if self.cross_double.crossup_detected() and self.obv_ema50.result > self.obv_ema50.last_result:
        #    return True

        if self.cross_long.crossup_detected() and self.obv_ema26.result > self.obv_ema26.last_result and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        if self.cross_short.crossup_detected() and self.obv_ema26.result > self.obv_ema26.last_result and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        if self.cross_double.crossup_detected() and self.obv_ema26.result > self.obv_ema26.last_result and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        #if self.trend_down_count > 10 and self.trend_up_count > 2 and self.trending_up:
        #    self.trend_up_count = 0
        #    self.trend_down_count = 0
        #    return True

        return False

    def sell_signal(self):
        if self.ema50.last_result == 0 or self.ema12.last_result == 0 or self.ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        #if self.kst.result > 0.0:
        #    return False

        if self.cross_short.crossdown_detected():
            return True

        if self.cross_long.crossdown_detected():
            return True

        if self.cross_double.crossdown_detected():
            return True

        if self.ema50.result > self.ema50.last_result and self.obv_ema50.result < self.obv_ema50.last_result:
            return True

        #if self.ema12.result > self.ema12.last_result and self.obv_ema12.result < self.obv_ema12.last_result:
        #    return True

        return False
