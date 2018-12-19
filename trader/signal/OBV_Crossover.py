from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.lib.CrossoverDouble import CrossoverDouble
from trader.signal.SignalBase import SignalBase

class OBV_Crossover(SignalBase):
    def __init__(self, accnt=None, symbol=None, win_short=12, win_med=26, win_long=50):
        super(OBV_Crossover, self).__init__(accnt, symbol)
        self.signal_name = "OBV_Crossover"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.cross_short = Crossover2(window=10)
        self.cross_long = Crossover2(window=10)
        self.cross_double = CrossoverDouble(window=10)
        self.obv = OBV()
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        #self.box = BOX()
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

    def pre_update(self, close, volume, ts, cache_db=None):
        obv_value = self.obv.update(close=close, volume=volume)
        self.prev_low = self.low
        self.prev_high = self.high

        value1 = self.obv_ema12.update(obv_value)
        value2 = self.obv_ema26.update(obv_value)
        value3 = self.obv_ema50.update(obv_value)

        self.cross_short.update(value1, value2)
        self.cross_long.update(value2, value3)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.cross_long.crossup_detected():
            return True

        if self.cross_short.crossup_detected():
            return True

        return False

    def sell_signal(self):
        if self.cross_long.crossdown_detected():
            return True

        if self.cross_short.crossdown_detected():
            return True

        return False
