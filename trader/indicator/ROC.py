# Compute the rate of change (ROC) from current price and price N values ago
from .IndicatorBase import IndicatorBase
from trader.indicator.SMA import SMA


class ROC(IndicatorBase):
    def __init__(self, window=10, use_sma=False):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window
        self.use_sma = use_sma
        self.sma = None
        if self.use_sma:
            self.sma = SMA(window=window)
        self.result = 0
        self.last_result = 0
        self.last_value = 0
        self.age = 0
        self.values = []

    def update(self, value):
        if not self.window:
            if not self.last_value:
                self.last_value = float(value)
                return self.result
            else:
                self.last_result = self.result
                self.result = 100.0 * (float(value - self.last_value)) / self.last_value
                self.last_value = float(value)
                return self.result

        if self.use_sma:
            if not self.last_value:
                self.last_value = float(value)
                return self.result
            else:
                self.last_result = self.result
                self.result = self.sma.update(100.0 * (float(value - self.last_value)) / self.last_value)
                self.last_value = float(value)
                return self.result

        if len(self.values) < self.window:
            self.values.append(float(value))
            self.result = 0
        else:
            old_value = self.values[int(self.age)]
            if old_value != 0:
                self.result = 100.0 * (float(value) - old_value) / old_value
            else:
                self.result = 0
            self.values[int(self.age)] = float(value)

        self.age = (self.age + 1) % self.window

        return self.result
