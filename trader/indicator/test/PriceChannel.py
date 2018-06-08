# Idea: True price channel with reverse linear projection
import numpy as np
from scipy.stats import linregress
from trader.indicator.MINMAX import MINMAX
from trader.indicator.SMA import SMA


class PriceSegment(object):
    def __init__(self, prices, slope, start, x):
        self.prices = np.array(prices)
        self.slope = slope
        self.start = start
        self.size = len(prices)
        self.x = np.array(x)
        self.line = []
        self.low_line = []
        self.high_line = []

    def get_regression_line(self):
        if len(self.line) == 0:
            self.line = (self.slope * self.x) + self.start
        return self.line

    def get_low_line(self):
        self.get_regression_line()
        diff = self.prices - self.line
        min_value = 0
        min_index = -1
        for i in range(0, len(diff)):
            if diff[i] < min_value:
                min_value = diff[i]
                min_index = i
        min_price = self.prices[min_index]
        start = min_price - self.slope * min_index
        self.low_line = (self.slope * self.x) + start
        return self.low_line

    def get_high_line(self):
        self.get_regression_line()
        diff = self.prices - self.line
        max_value = 0
        max_index = -1
        for i in range(0, len(diff)):
            if diff[i] > max_value:
                max_value = diff[i]
                max_index = i
        max_price = self.prices[max_index]
        start = max_price - self.slope * max_index
        self.high_line = (self.slope * self.x) + start
        return self.high_line


class PriceChannel(object):
    def __init__(self, window=50):
        self.window = window
        self.prices = []
        self.sma_prices = []
        self.prices_x = []
        self.segments = []
        self.win_prices = []
        self.minmax = MINMAX(100)
        self.age = 0
        self.sma = SMA(50)
        self.total_age = 0
        self.result = []
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.low_count = 0
        self.high_count = 0
        self.up = False
        self.down = False

    def reset(self):
        self.prices = []
        self.prices_x = []
        self.sma_prices = []
        self.age = 0
        self.total_age = 0

    def update(self, price):
        self.prev_low = self.low
        self.prev_high = self.high
        self.low, self.high = self.minmax.update(price)

        if self.low_count > 2 and self.high_count > 5:
            self.high_count = 0
            self.low_count = 0
            self.down = True
        elif self.low_count > 5 and self.high_count > 2:
            self.high_count = 0
            self.low_count = 0
            self.up = True

        if self.down or self.up:
            slope = (self.sma_prices[-1] - self.sma_prices[0]) / (self.prices_x[-1] - self.prices_x[0])
            start = self.sma_prices[0]
            s = PriceSegment(self.prices, slope=slope, start=start, x=self.prices_x)
            center = s.get_regression_line()
            high = s.get_high_line()
            low = s.get_low_line()
            self.result = [center, low, high]
            self.segments.append(s)
            self.reset()
        else:
            self.result = []

        if len(self.win_prices) < self.window:
            self.win_prices.append(float(price))
            self.prices.append(float(price))
            self.prices_x.append(self.total_age)
        else:
            self.win_prices[int(self.age)] = float(price)
            self.prices.append(float(price))
            self.prices_x.append(self.total_age)
            if self.low < self.prev_low:
                self.low_count += 1
            elif self.high > self.prev_high:
                self.high_count += 1

            self.sma_prices.append(self.sma.update(price))

            # mixed result so discard
            if self.low_count == 3 and self.high_count == 3:
                self.low_count = 0
                self.high_count = 0

        self.age = (self.age + 1) % self.window
        self.total_age = self.total_age + 1

        return self.result

    def split_down(self):
        if self.down:
            self.down = False
            return True
        return False

    def split_up(self):
        if self.up:
            self.up = False
            return True
        return False

    def get_regression_line(self):
        slope = (self.sma_prices[-1] - self.sma_prices[0]) / (self.prices_x[-1] - self.prices_x[0])
        intercept = self.sma_prices[0]
        #slope, intercept, r_value, p_value, std_err = linregress(self.prices_x, self.prices)
        x = np.array(self.prices_x)
        result = slope * x + intercept
        return result

    def values_between_lines(self, values, low_start, low_end, high_start, high_end, count):
        low_slope = (low_end - low_start) / count
        high_slope = (high_end - high_start) / count
        for i in range(0, count):
            low = i * low_slope + low_start
            high = i * high_slope + high_start
            if values[i] < low:
                return -1, i, values[i]
            if values[i] > high:
                return 1, i, values[i]
        return 0, 0, 0
