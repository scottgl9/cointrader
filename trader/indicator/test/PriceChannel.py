# Idea: True price channel with reverse linear projection
import numpy as np
from scipy.stats import linregress
from trader.indicator.MINMAX import MINMAX

class PriceSegment(object):
    def __init__(self, prices, slope, start, x):
        self.prices = prices
        self.slope = slope
        self.start = start
        self.size = len(prices)
        self.x = np.array(x)

    def get_values(self):
        return (self.slope * self.x) + self.start

class PriceChannel(object):
    def __init__(self, window=50):
        self.window = window
        self.prices = []
        self.prices_x = []
        self.segments = []
        self.win_prices = []
        self.minmax = MINMAX(100)
        self.age = 0
        self.total_age = 0
        self.result = []
        self.low = 0
        self.high = 0
        self.prev_low = 0
        self.prev_high = 0
        self.low_count = 0
        self.high_count = 0

    def update(self, price):
        self.prev_low = self.low
        self.prev_high = self.high
        self.low, self.high = self.minmax.update(price)

        if len(self.win_prices) < self.window:
            self.win_prices.append(float(price))
            self.prices.append(float(price))
            self.prices_x.append(self.total_age)
        else:
            self.result = []
            self.win_prices[int(self.age)] = float(price)
            self.prices.append(float(price))
            self.prices_x.append(self.total_age)
            if self.low < self.prev_low:
                self.low_count += 1
            elif self.high > self.prev_high:
                self.high_count += 1

            if self.low_count == 3 and self.high_count == 3:
                self.low_count = 0
                self.high_count = 0

        self.age = (self.age + 1) % self.window
        self.total_age = self.total_age + 1

        return self.result

    def split_down(self):
        if self.low_count > 2 and self.high_count > 5:
            self.high_count = 0
            self.low_count = 0
            return True
        return False

    def split_up(self):
        if self.low_count > 5 and self.high_count > 2:
            self.high_count = 0
            self.low_count = 0
            return True
        return False

    def line_values(self, start, end, count):
        values = []
        slope = (end - start) / count
        for i in range(0, count):
            values.append(i * slope + start)
        return values

    def values_between_lines(self, values, low_start, low_end, high_start, high_end, count):
        #if (low_end - low_start) == 0 or (high_end - high_start) == 0:
        #    return 0,0,0
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

    def recompute(self):
        if self.cur_low == 0 or self.cur_high == 0:
            self.cur_low = min(self.win_prices)
            self.cur_high = max(self.win_prices)
            slope_low = (self.cur_low - self.start_low) / self.total_age
            slope_high = (self.cur_high - self.start_high) / self.total_age
            if abs(slope_low) < abs(slope_high):
                self.slope = slope_low
                self.start_low = self.cur_low - (self.slope * self.total_age)
            else:
                self.slope = slope_high
                self.start_high = self.cur_high - (self.slope * self.total_age)
        else:
            cur_low = self.slope * self.total_age + self.start_low
            cur_high = self.slope * self.total_age + self.start_high
            if min(self.win_prices) < cur_low:
                cur_low = min(self.win_prices)
            if max(self.win_prices) > cur_high:
                cur_high = max(self.win_prices)
            result, index, lvalue = self.values_between_lines(self.prices,
                                                              self.start_low,
                                                              cur_low,
                                                              self.start_high,
                                                              cur_high,
                                                              self.total_age)
            if result != 0:
                if result == -1:
                    # new low value
                    cur_low = self.prices[index]
                    if index == 0:
                        self.cur_low = cur_low
                    else:
                        slope_low = (cur_low - self.start_low) / index
                        self.slope = slope_low
                        # try adjusting upper line down
                        start_high = self.cur_high - (slope_low * index)
                        result, index, lvalue = self.values_between_lines(self.prices,
                                                                          self.start_low,
                                                                          cur_low,
                                                                          start_high,
                                                                          cur_high,
                                                                          self.total_age)
                        if result == 0:
                            self.start_high = start_high
                            self.slope = slope_low
                            self.cur_high = (self.slope * self.total_age) + self.start_high
                        else:
                            # didn't work, adjust start_low down
                            self.cur_low = cur_low
                            self.start_low = self.cur_low - (self.slope * self.total_age)
                elif result == 1:
                    # new high value
                    cur_high = self.prices[index]
                    if index == 0:
                        self.cur_high = cur_high
                    else:
                        slope_high = (cur_high - self.start_high) / index
                        # try adjusting lower line up
                        start_low = self.cur_low - (slope_high * index)
                        result, index, lvalue = self.values_between_lines(self.prices,
                                                                          start_low,
                                                                          cur_low,
                                                                          self.start_high,
                                                                          cur_high,
                                                                          self.total_age)
                        if result == 0:
                            self.start_low = start_low
                            self.slope = slope_high
                            self.cur_low = (self.slope * self.total_age) + self.start_low
                        else:
                            # didn't work, adjust start_high up
                            self.cur_high = cur_high
                            self.start_high = self.cur_high - (self.slope * self.total_age)
            else:
                self.cur_low = cur_low
                self.cur_high = cur_high
