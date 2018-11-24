from trader.indicator.EMA import EMA
from trader.indicator.OBV import OBV
from trader.lib.Crossover2 import Crossover2
from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class Currency_EMA_Long(SignalBase):
    def __init__(self):
        super(Currency_EMA_Long, self).__init__()
        self.ema1 = EMA(100, scale=24)
        self.ema2 = EMA(200, scale=24)
        self.cross_short = Crossover2(window=10)
        self.cross_long = Crossover2(window=10)
        self.obv = OBV()
        self.obv_ema12 = EMA(12, scale=24)
        self.obv_ema26 = EMA(26, scale=24, lag_window=5)
        self.obv_ema50 = EMA(50, scale=24, lag_window=5)
        self.set_flag(SignalBase.FLAG_SELL_ALL)

    def pre_update(self, close, volume, ts):
        symbol = self.get_symbol()
        if symbol != "ETHBTC" and symbol != "BNBBTC":
            return
        self.ema1.update(float(close))
        self.ema2.update(float(close))
        self.cross_long.update(self.ema1.result, self.ema2.result)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.cross_long.crossup_detected():
            return True
        return False

    def sell_long_signal(self):
        if self.cross_long.crossdown_detected():
            return True
        return False

    def sell_signal(self):
        if self.cross_long.crossdown_detected():
            return True
        return False
