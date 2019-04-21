from .IndicatorBase import IndicatorBase
from trader.lib.CircularArray import CircularArray


class MINMAX(IndicatorBase):
    def __init__(self, window=50, count=0):
        IndicatorBase.__init__(self, use_close=True)
        self.values = []
        self.maximums = CircularArray(count)
        self.minimums = CircularArray(count)
        self.count = count
        self.window = window
        self.age = 0
        self.minimum = 0
        self.maximum = 0

    def update(self, value, ts=0):
        if len(self.values) < self.window:
            self.values.append(float(value))
        else:
            self.values[int(self.age)] = float(value)

        self.minimum = min(self.values)
        self.maximum = max(self.values)

        if self.count != 0:
            if len(self.minimums.carray) == 0 or self.minimum < self.minimums.min():
                self.minimums.add(self.minimum)
            else:
                self.minimum = self.minimums.min()
            if len(self.maximums.carray) == 0 or self.maximum > self.maximums.max():
                self.maximums.add(self.maximum)
            else:
                self.maximum = self.maximums.max()

        self.age = (self.age + 1) % self.window

        return self.minimum, self.maximum
