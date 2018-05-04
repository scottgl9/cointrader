from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.Crossover import Crossover


class EMA_OBV_Crossover(object):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.ema12 = EMA(self.win_short, scale=24, lagging=True)
        self.ema26 = EMA(self.win_med, scale=24, lagging=True)
        self.ema50 = EMA(self.win_long, scale=24, lagging=True, lag_window=5)
        self.cross_short = Crossover()
        self.cross_long = Crossover()

        self.obv = OBV()
        self.obv_ema12 = EMA(self.win_short, scale=24, lagging=True)
        self.obv_ema26 = EMA(self.win_med, scale=24, lagging=True)
        self.obv_ema50 = EMA(self.win_long, scale=24, lagging=True, lag_window=5)

    def pre_update(self, close, volume):
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        value1 = self.ema12.update(close)
        value2 = self.ema26.update(close)
        value3 = self.ema50.update(close)
        self.cross_short.update(value1, value2)
        self.cross_long.update(value2, value3)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.ema50.last_result == 0 or self.ema12.last_result == 0 or self.ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.cross_long.crossup_detected() and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        if self.cross_short.crossup_detected() and self.obv_ema26.result > self.obv_ema26.last_result: #and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        return False

    def sell_signal(self):
        if self.ema50.last_result == 0 or self.ema12.last_result == 0 or self.ema26.last_result == 0:
            return False

        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema26.result > self.obv_ema26.last_result and self.ema26.result > self.ema26.last_result:
            return False

        if self.cross_short.crossdown_detected():
            return True

        if self.cross_long.crossdown_detected():
            return True

        if self.ema50.result > self.ema50.last_result and self.obv_ema50.result < self.obv_ema50.last_result:
            return True

        return False
