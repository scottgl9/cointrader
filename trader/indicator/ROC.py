# Compute the rate of change (ROC) from current price and price N values ago
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.SMA import SMA


class ROC(IndicatorBase):
    def __init__(self, window=10, smoother=None):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window
        self.result = 0
        self.last_result = 0
        self.last_value = 0
        self.age = 0
        self.values = []
        self.smoother = smoother

    def update(self, close):
        if len(self.values) < self.window:
            self.values.append(float(close))
            self.result = 0
        else:
            old_value = self.values[int(self.age)]
            if old_value:
                result = 100.0 * (float(close) - old_value) / old_value
                if self.smoother:
                    self.result = self.smoother.update(result)
                else:
                    self.result = result
            else:
                self.result = 0
            self.values[int(self.age)] = float(close)
            self.age = (self.age + 1) % self.window

        return self.result
