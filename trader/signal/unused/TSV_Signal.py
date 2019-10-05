from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.indicator.ZLEMA import ZLEMA
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.Crossover import Crossover
from trader.lib.PeakValleyDetect import PeakValleyDetect
from trader.lib.struct.SignalBase import SignalBase

class TSV_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None, window=26):
        super(TSV_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "TSV_Signal"
        self.window = window

        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24, lag_window=5)
        self.ema50 = EMA(50, scale=24, lag_window=5)

        self.tsv = MovingTimeSegment(seconds=1000)
        self.tsv_cross_zero = Crossover(window=10)
        self.tsv_ema = ZLEMA(100, scale=24)
        self.detector = PeakValleyDetect()

    def pre_update(self, close, volume, ts):
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

        self.ema12.update(close)
        self.ema26.update(close)
        value1 = self.ema50.update(close)

        self.tsv.update(close, ts)
        if self.tsv.ready():
            pchange = self.tsv.percent_change()
            if pchange != None:
                self.tsv_ema.update(self.tsv.percent_change())
                self.tsv_cross_zero.update(self.tsv_ema.result, 0)
                self.detector.update(self.tsv_ema.result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result < self.obv_ema26.last_result and self.ema26.result < self.ema26.last_result:
            return False

        if self.obv_ema12.result < self.obv_ema12.last_result and self.ema12.result < self.ema12.last_result:
            return False

        if self.tsv_cross_zero.crossup_detected():
            return True

        if self.detector.valley_detect():
            return True

        return False

    def sell_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False
        if self.tsv_cross_zero.crossdown_detected():
            return True

        if self.detector.peak_detect():
            return True

        return False
