from trader.indicator.SMA import SMA
from trader.lib.ValueLag import ValueLag

class EMA:
    def __init__(self, weight=26, scale=1.0, lagging=False, lag_window=5):
        self.result = 0.0
        self.last_result = 0.0
        self.weight = float(weight)
        self.scale = scale
        self.sma = SMA(weight)
        self.lagging = lagging
        self.value_lag = None
        if self.lagging:
            self.value_lag = ValueLag(window=lag_window)

    def update(self, price):
        if self.result == 0.0:
            self.last_result = self.result
            self.result = self.sma.update(price)
            return self.result
        else:
            k = 2.0 / (self.weight * self.scale + 1.0)
            y = self.result

            if self.lagging:
                self.last_result = self.value_lag.update(self.result)
            else:
                self.last_result = self.result

            self.result = self.sma.update(price) * k + y * (1.0 - k)
            return self.result
