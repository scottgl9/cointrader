# Idea: True price channel with reverse linear projection


class PriceChannel(object):
    def __init__(self, window=50):
        self.window = window
        self.prices = []
        self.win_prices = []
        self.age = 0
        self.total_age = 0
        self.start_low = 0
        self.start_high = 0
        self.cur_low = 0
        self.cur_high = 0
        self.slope = 0

    def update(self, price):
        if len(self.win_prices) < self.window:
            self.win_prices.append(float(price))
            self.prices.append(float(price))
        else:
            self.win_prices[int(self.age)] = float(price)
            self.prices.append(float(price))
            if self.age == 0:
                if self.start_low == 0 or self.start_high == 0:
                    self.start_low = min(self.prices)
                    self.start_high = max(self.prices)
                else:
                    self.recompute()

        self.age = (self.age + 1) % self.window
        self.total_age = self.total_age + 1

        return self.start_low, self.start_high, self.cur_low, self.cur_high

    def line_values(self, start, end, count):
        values = []
        slope = (end - start) / count
        for i in range(0, count):
            values.append(i * slope + start)
        return values

    def values_between_lines(self, values, low_start, low_end, high_start, high_end, count):
        if (low_end - low_start) == 0 or (high_end - high_start) == 0:
            return 0,0,0
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
            result, index, lvalue = self.values_between_lines(self.prices,
                                                              self.start_low,
                                                              cur_low,
                                                              self.start_high,
                                                              cur_high,
                                                              self.total_age)
            if result != 0:
                if result == -1:
                    # new low value
                    cur_low = min(self.win_prices)
                    slope_low = (cur_low - self.start_low) / self.total_age
                    # try adjusting upper line down
                    start_high = self.cur_high - (slope_low * self.total_age)
                    result, index, lvalue = self.values_between_lines(self.prices,
                                                                      self.start_low,
                                                                      cur_low,
                                                                      start_high,
                                                                      cur_high,
                                                                      self.total_age)
                    if result == 0:
                        self.start_high = start_high
                        self.slope = slope_low
                    else:
                        # didn't work, adjust start_low down
                        self.cur_low = cur_low
                        self.start_low = self.cur_low - (self.slope * self.total_age)

                elif result == 1:
                    # new high value
                    cur_high = max(self.win_prices)
                    slope_high = (cur_high - self.start_high) / self.total_age
                    # try adjusting lower line up
                    start_low = self.cur_low - (slope_high * self.total_age)
                    result, index, lvalue = self.values_between_lines(self.prices,
                                                                      start_low,
                                                                      cur_low,
                                                                      self.start_high,
                                                                      cur_high,
                                                                      self.total_age)
                    if result == 0:
                        self.start_low = start_low
                        self.slope = slope_high
                    else:
                        # didn't work, adjust start_high up
                        self.cur_high = cur_high
                        self.start_high = self.cur_high - (self.slope * self.total_age)
            else:
                self.cur_low = cur_low
                self.cur_high = cur_high
