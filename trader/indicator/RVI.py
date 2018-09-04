# Relative Volatility Index (RVI)
from trader.indicator.SMMA import SMMA
from trader.indicator.STDDEV import STDDEV


class RVI:
    def __init__(self, window=20):
        self.window = window
        self.stddev = STDDEV(window=window)
        self.avgU = SMMA(self.window)
        self.avgD = SMMA(self.window)
        self.last_close = 0
        self.result = 0
        self.age = 0

    def update(self, close):
        if self.last_close == 0:
            self.last_close = float(close)
            return self.result

        std_value = self.stddev.update(float(close))

        if float(close) > self.last_close:
            u = std_value
            d = 0.0
        else:
            u = 0.0
            d = std_value

        Usum = self.avgU.update(u)
        Dsum = self.avgD.update(d)

        self.result = 100.0 * Usum / (Usum + Dsum)

        return self.result
