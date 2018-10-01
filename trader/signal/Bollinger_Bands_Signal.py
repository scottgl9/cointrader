from trader.indicator.BB import BollingerBands
from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.signal.SignalBase import SignalBase

class Bollinger_Bands_Signal(SignalBase):
    def __init__(self, win_short=12, win_med=26, win_long=50):
        super(Bollinger_Bands_Signal, self).__init__()
        self.signal_name = "Bollinger_Bands_Signal"
        self.win_short = win_short
        self.win_med = win_med
        self.win_long = win_long
        self.bb = BollingerBands(dev_count=3.0)
        self.obv = OBV()
        self.ema12 = EMA(self.win_short, scale=24)
        self.obv_ema12 = EMA(self.win_short, scale=24)
        self.obv_ema26 = EMA(self.win_med, scale=24, lag_window=5)
        self.obv_ema50 = EMA(self.win_long, scale=24, lag_window=5)
        self.close_price = 0

    def pre_update(self, close, volume, ts):
        self.close_price = close
        self.bb.update(close)
        obv_value = self.obv.update(close=close, volume=volume)
        self.obv_ema12.update(obv_value)
        self.obv_ema26.update(obv_value)
        self.obv_ema50.update(obv_value)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema50.result < self.obv_ema50.last_result:
            return False

        if self.obv_ema26.result <= self.obv_ema26.last_result:
            return False

        if self.obv_ema12.result <= self.obv_ema12.last_result:
            return False

        if self.bb.low_band != 0 and self.close_price <= self.bb.low_band and self.obv_ema26.result > self.obv_ema26.last_result and self.obv_ema50.result > self.obv_ema50.last_result:
            return True

        return False

    def sell_signal(self):
        if self.obv_ema50.last_result == 0 or self.obv_ema12.last_result == 0 or self.obv_ema26.last_result == 0:
            return False

        if self.obv_ema12.result > self.obv_ema12.last_result and self.ema12.result > self.ema12.last_result:
            return False

        if self.bb.high_band != 0 and self.close_price >= self.bb.high_band:
            return True

        return False

