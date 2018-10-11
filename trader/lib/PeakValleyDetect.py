# Peak / Valley Detection
from trader.lib.CircularArray import CircularArray


class PeakValleyDetect(object):
    def __init__(self, window=50):
        self.values = []
        self.slopes = []
        self.window = window
        self.age = 0
        self.slope_age = 0
        self.negative_slope = False
        self.positive_slope = False
        self.peak = False
        self.valley = False
        self.last_peak = 0.0
        self.last_valley = 0.0

    def update(self, value):
        if float(value) in self.values:
            return
        if len(self.values) < self.window:
            self.values.append(float(value))
        else:
            old_value = self.values[int(self.age)]
            self.values[int(self.age)] = float(value)

            if len(self.slopes) < self.window:
                self.slopes.append(float(value) - old_value)
                self.slope_age = (self.slope_age + 1) % self.window
            else:
                self.slopes[int(self.slope_age)] = float(value) - old_value
                if self.slope_age % self.window == 0:
                    negative_slope = True
                    positive_slope = True
                    for slope in self.slopes:
                        if slope < 0.0:
                            positive_slope = False
                        elif slope > 0.0:
                            negative_slope = False

                    if not self.negative_slope and not self.positive_slope:
                        if negative_slope:
                            self.negative_slope = True
                        elif positive_slope:
                            self.positive_slope = True
                    elif self.negative_slope and not self.positive_slope:
                        if positive_slope and not negative_slope:
                            if (self.last_valley == 0 or float(value) < self.last_valley): # and self.percent_change() > 0.01:
                                self.valley = True
                                self.negative_slope = False
                                self.last_valley = float(value)
                    elif not self.negative_slope and self.positive_slope:
                        if negative_slope and not positive_slope:
                            if (self.last_peak == 0 or float(value) > self.last_peak): # and self.percent_change() > 0.01:
                                self.peak = True
                                self.positive_slope = False
                                self.last_peak = float(value)

                self.slope_age = (self.slope_age + 1) % self.window

        self.age = (self.age + 1) % self.window

    def percent_change(self):
        low = min(self.values)
        high = max(self.values)
        return 100 * (high - low) / low

    def peak_detect(self, clear=True):
        if self.peak:
            if clear:
                self.peak = False
            return True
        return False

    def valley_detect(self, clear=True):
        if self.valley:
            if clear:
                self.valley = False
            return True
        return False
