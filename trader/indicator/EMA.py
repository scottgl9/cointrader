from trader.indicator.SMA import SMA
from trader.lib.ValueLag import ValueLag


class EMA:
    def __init__(self, weight=26, scale=1.0, lagging=False, lag_window=3):
        self.result = 0.0
        self.last_result = 0.0
        self.weight = float(weight)
        self.scale = scale
        self.sma = SMA(weight)
        self.count = 0
        self.esf = 0.0
        self.lagging = lagging
        self.value_lag = None
        if self.lagging:
            self.value_lag = ValueLag(window=lag_window)

    def update(self, price):
        if self.count < self.weight:
            self.result = self.sma.update(float(price))
            self.count += 1
            return self.result

        if self.result == 0:
            esf = 2.0 / (self.weight * self.scale)
            last_result = self.sma.update(float(price))
            self.result = float(price) * esf + last_result - 1 * (1 - esf)
        else:
            last_result = self.result

            if self.esf == 0.0:
                self.esf = 2.0 / (self.weight * self.scale + 1.0)

            if self.lagging:
                self.last_result = self.value_lag.update(self.result)
            else:
                self.last_result = self.result

            self.result = last_result + self.esf * (float(price) - last_result)

        return self.result
