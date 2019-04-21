from .IndicatorBase import IndicatorBase
from trader.indicator.EMA import EMA


class DEMA(IndicatorBase):
    def __init__(self, weight=12.0):
        IndicatorBase.__init__(self, use_close=True)
        self.result = 0.0
        self.weight = weight
        self.inner = EMA(self.weight)
        self.outer = EMA(self.weight)

    def update(self, price, ts=0):
        self.inner.update(price)
        self.outer.update(self.inner.result)
        self.result = 2.0 * self.inner.result - self.outer.result
