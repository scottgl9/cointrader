# Idea: True price channel with reverse linear projection
import numpy as np
from scipy.stats import linregress
from trader.indicator.MINMAX import MINMAX
from trader.indicator.SMA import SMA


class PriceSegment(object):
    def __init__(self, prices, start, end, x):
        self.prices = np.array(prices)
        self.start = start
        self.end = end
        self.size = len(prices)
        self.x = np.array(x)
        self.line = []
        self.low_line = []
        self.high_line = []
        self.slope = (end - start) / (self.x[-1] - self.x[0])
        self.low_diff = 0
        self.high_diff = 0
        self.low_start = 0
        self.high_start = 0

    def add(self, prices, x, end):
        self.line = []
        self.low_line = []
        self.high_line = []
        self.prices = np.append(self.prices, prices)
        self.size = len(self.prices)
        self.x = np.array(range(0, self.size)) #np.append(self.x, x)
        self.end = end
        self.slope = (self.end - self.start) / (self.x[-1] - self.x[0])
        self.set_regression_line()
        self.get_low_line()
        self.get_high_line()

    def set_regression_line(self):
        self.line = (self.slope * self.x) + self.start

    def get_regression_line(self):
        if len(self.line) == 0:
            self.set_regression_line()
        return self.line

    def get_low_line(self, start=0):
        if start != 0:
            self.low_line = (self.slope * self.x) + start
        else:
            self.low_line = (self.slope * self.x) + self.low_start
        return self.low_line

    def get_high_line(self, start=0):
        if start != 0:
            self.high_line = (self.slope * self.x) + start
        else:
            self.high_line = (self.slope * self.x) + self.high_start
        return self.high_line

    def compute_low_start(self):
        if len(self.low_line) == 0:
            self.get_regression_line()
            diff = self.prices - self.line
            min_value = 0
            min_index = -1
            for i in range(0, len(diff)):
                if diff[i] < min_value:
                    min_value = diff[i]
                    min_index = i
            self.low_diff = min_value
            min_price = self.prices[min_index]
            self.low_start = min_price - self.slope * min_index
        return self.low_start

    def compute_high_start(self):
        if len(self.high_line) == 0:
            self.get_regression_line()
            diff = self.prices - self.line
            max_value = 0
            max_index = -1
            for i in range(0, len(diff)):
                if diff[i] > max_value:
                    max_value = diff[i]
                    max_index = i
            self.high_diff = max_value
            max_price = self.prices[max_index]
            self.high_start = max_price - self.slope * max_index
        return self.high_start

    def values_between_lines(self, values):
        test_values = np.append(self.prices, values)
        count = len(test_values)
        low_slope = self.slope
        high_slope = self.slope
        for i in range(0, count):
            low = i * low_slope + self.low_start
            high = i * high_slope + self.high_start
            if test_values[i] < low:
                return False
            if test_values[i] > high:
                return False
        return True


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
        self.last_center_start = 0
        self.last_center_end = 0
        self.last_high_start = 0
        self.last_high_end = 0
        self.last_low_start = 0
        self.last_low_end = 0
        self.last_slope = 0
        self.debug_age = 0

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


            #s = PriceSegment(self.prices, start=start, end=end, x=self.prices_x)

            s = self.process_segments()

            center = s.get_regression_line()
            slope = s.slope

            high = s.get_high_line()
            low = s.get_low_line()
            #pcenter = 100.0 * (center[0] - low[0]) / (high[0] - low[0])

            self.last_center_start = center[0]
            self.last_center_end = center[-1]
            self.last_high_start = high[0]
            self.last_high_end = high[-1]
            self.last_low_start = low[0]
            self.last_low_end = low[-1]
            self.last_slope = slope
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
        self.debug_age = self.debug_age + 1

        return self.result

    def process_segments(self):
        # adjust high and low lines to be equal distance from center line
        #for s in self.segments:


        if len(self.segments) > 0:
            s = self.segments[-1]
            if s.values_between_lines(self.prices):
                s.add(self.prices, self.prices_x, self.sma_prices[-1])
            else:
                start = self.sma_prices[0]
                end = self.sma_prices[-1]
                s = PriceSegment(self.prices, start=start, end=end, x=self.prices_x)
                s.get_regression_line()
                s.compute_high_start()
                s.compute_low_start()
                if abs(s.low_diff) < abs(s.high_diff):
                    s.low_start -= abs(s.high_diff) - abs(s.low_diff)
                    s.low_diff = s.high_diff
                elif abs(s.low_diff) > abs(s.high_diff):
                    s.high_start += abs(s.low_diff) - abs(s.high_diff)
                    s.high_diff = s.low_diff
                s.get_low_line()
                s.get_high_line()
                self.segments.append(s)
                # reverse channel size propagation
                for i in range(len(self.segments)-1, 0, -1):
                    s1 = self.segments[i - 1]
                    s2 = self.segments[i]
                    s2low = s2.get_low_line()
                    s2high = s2.get_high_line()
                    s1low = s1.get_low_line()   # segment before s2
                    s1high = s1.get_high_line()
                    if s1low[-1] >= s2low[0] and s1high[-1] <= s2high[0]:
                        s1.low_start -= s1low[-1] - s2low[0]
                        s1.high_start += s2high[0] - s1high[-1]
                        s1.get_low_line()
                        s1.get_high_line()
        else:
            start = self.sma_prices[0]
            end = self.sma_prices[-1]
            s = PriceSegment(self.prices, start=start, end=end, x=self.prices_x)
            s.get_regression_line()
            s.compute_high_start()
            s.compute_low_start()
            s.get_low_line()
            s.get_high_line()
            self.segments.append(s)
        return s

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

    def get_values(self):
        result = []
        for s in self.segments:
            center = s.get_regression_line()
            low = s.get_low_line()
            high = s.get_high_line()
            result.append([center, low, high])
        return result

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
