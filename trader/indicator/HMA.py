# Hull Moving Average
from .IndicatorBase import IndicatorBase
import numpy as np
from trader.indicator.WMA import WMA


class HMA(IndicatorBase):
    def __init__(self, window, scale=1.0):
        IndicatorBase.__init__(self, use_close=True)
        self.wma1 = WMA(window=window/2, scale=scale)
        self.wma2 = WMA(window=window, scale=scale)
        self.wma3 = WMA(window=int(np.sqrt(float(window))), scale=scale)
        self.window = window
        self.result = 0.0

    def update(self, value, ts=0):
        result1 = self.wma1.update(float(value))
        result2 = self.wma2.update(float(value))
        self.result = self.wma3.update(2.0 * result1 - result2)
        return self.result
