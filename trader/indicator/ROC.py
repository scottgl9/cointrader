# Compute the rate of change (ROC) from current price and price N values ago
from .IndicatorBase import IndicatorBase


class ROC(IndicatorBase):
    def __init__(self, window=10):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window
        self.result = 0.0
        self.age = 0
        self.values = []

    def update(self, value, ts=0):
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
