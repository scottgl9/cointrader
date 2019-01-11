# Relative Strength Index (RS)
from trader.indicator.SMA import SMA
from trader.indicator.EMA import EMA


class RSI:
    def __init__(self, window=14, smoother=None):
        self.window = window

        self.avgU = SMA(self.window)
        self.avgD = SMA(self.window)
        self.prev_avgU = 0
        self.prev_avgD = 0
        self.last_price = 0
        self.rs = 0
        self.result = 0
        self.smoother = smoother

    def update(self, price, ts=0):
        if self.last_price == 0:
            self.last_price = float(price)
            return self.result

        if float(price) > self.last_price:
            u = float(price) - self.last_price
            d = 0.0
        else:
            u = 0.0
            d = self.last_price - float(price)

        self.prev_avgU = self.avgU.result
        self.prev_avgD = self.avgD.result

        self.avgU.update(u)
        self.avgD.update(d)

        if self.avgU.length() < self.window:
            self.last_price = float(price)
            return self.result

        if self.avgD.result == 0:
            return self.result
        else:
            # first RS
            if self.rs == 0:
                self.rs = self.avgU.result / self.avgD.result
            else:
                # smoothed RS (Don't really need to divide both by window size since is a ratio
                self.rs = (13.0 * self.prev_avgU + u) / (13.0 * self.prev_avgD + d)

        if self.smoother:
            self.result = self.smoother.update(100.0 - (100.0 / (1.0 + self.rs)))
        else:
            self.result = 100.0 - (100.0 / (1.0 + self.rs))
        self.last_price = float(price)

        return self.result
