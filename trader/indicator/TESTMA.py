# idea I have for smoothing a moving average
from trader.lib.CircularArray import CircularArray

# Idea of channel linear regression lines:
# - each time price is updated, add to circular array of size
#   window, take minimum of prices in window, and add result to
# array of low_prices. Do the same except use max for high_prices

# Find direction of the trend:
# if minimum of high_prices <= maximum of low_prices: direction = -1
# if maximum of low_prices >= minimum of high_prices: direction = 1
from trader.indicator.EMA import EMA

class TESTMA(object):
    def __init__(self, window=50, window2=50):
        self.window = window
        self.window2 = window2
        self.values = CircularArray(window=window)
        self.low_prices = CircularArray(window=window2)
        self.high_prices = CircularArray(window=window2)
        self.low_prices_min = CircularArray(window=5)
        self.high_prices_max = CircularArray(window=5)
        self.age = 0
        self.age2 = 0
        self.segment_age = 0
        self.result = 0
        self.direction = 0
        self.last_direction = 0
        self.min_low_prices = 0
        self.last_min_low_prices = 0
        self.max_high_prices = 0
        self.last_max_high_prices = 0
        self.upward_reversal = False
        self.downward_reversal = False

    def update(self, value):
        if float(value) not in self.values.values():
            self.values.add(float(value))
        values = self.values.values()

        if len(values) == self.window:
            self.low_prices.add(min(values))
            self.high_prices.add(max(values))

        low_prices = self.low_prices.values()
        high_prices = self.high_prices.values()

        if len(self.low_prices) < 1 or len(self.high_prices) < 1:
            return 0.0, 0.0

        self.last_min_low_prices = self.min_low_prices
        self.last_max_high_prices = self.max_high_prices
        self.min_low_prices = min(low_prices)
        self.max_high_prices = max(high_prices)

        if self.min_low_prices == self.last_min_low_prices:
            return 0.0, 0.0
        if self.max_high_prices == self.last_max_high_prices:
            return 0.0, 0.0

        if len(high_prices) != 0:
            if self.min_low_prices < self.last_min_low_prices:
                if self.direction == -1 and self.last_direction == 1:
                    self.downward_reversal = True
                    print("downward reversal {}".format(self.min_low_prices))

                self.last_direction = self.direction
                self.direction = -1
            elif self.min_low_prices > self.last_min_low_prices:
                if self.direction == 1 and self.last_direction == -1:
                    self.upward_reversal = True
                    print("upward reversal {}".format(self.min_low_prices))
                self.last_direction = self.direction
                self.direction = 1

        return self.min_low_prices, self.max_high_prices

    def valley(self):
        if self.upward_reversal:
            self.upward_reversal = False
            return True
        return False

    def peak(self):
        if self.upward_reversal:
            self.upward_reversal = False
            return True
        return False
