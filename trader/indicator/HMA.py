# Hull Moving Average

import numpy as np
from trader.indicator.WMA import WMA


class HMA(object):
    def __init__(self, window, scale=1.0):
        self.wma1 = WMA(window=window/2, scale=scale)
        self.wma2 = WMA(window=window, scale=scale)
        self.wma3 = WMA(window=int(np.sqrt(float(window))), scale=scale)
        self.window = window
        self.result = 0.0

    def update(self, value):
        result1 = self.wma1.update(float(value))
        result2 = self.wma2.update(float(value))
        self.result = self.wma3.update(2.0 * result1 - result2)
        return self.result
