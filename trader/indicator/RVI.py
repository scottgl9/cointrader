# Relative Volatility Index (RVI)
from trader.indicator.SMA import SMA
from trader.indicator.STDDEV import STDDEV


class RVI:
    def __init__(self, window=20):
        self.window = window
        self.stddev = STDDEV(window=window)
        self.avgU = SMA(self.window)
        self.avgD = SMA(self.window)
        self.last_close = 0
        self.result = 0
        self.age = 0

    def update(self, close, ts=0):
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

        if Usum == 0 and Dsum == 0:
            self.result = 0
        else:
            self.result = 100.0 * Usum / (Usum + Dsum)

        self.last_close = close

        return self.result
