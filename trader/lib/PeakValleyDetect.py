# Peak / Valley Detection


class PeakValleyDetect(object):
    def __init__(self, slope_window=30, window=400):
        self.values = []
        self.slopes = []
        self.slope_window = slope_window
        self.window = window
        self.age = 0
        self.slope_age = 0
        self.negative_slope = False
        self.negative_slope_count = 0
        self.last_negative_slope_count = 0
        self.positive_slope = False
        self.positive_slope_count = 0
        self.last_positive_slope_count = 0
        self.peak = False
        self.valley = False
        self.last_peak = 0.0
        self.last_valley = 0.0

    def update(self, value):
        if float(value) in self.values:
            return
        if len(self.values) < self.slope_window:
            self.values.append(float(value))
        else:
            old_value = self.values[int(self.age)]
            self.values[int(self.age)] = float(value)

            if len(self.slopes) < self.window:
                self.slopes.append(float(value) - old_value)
            else:
                self.slopes[int(self.slope_age)] = float(value) - old_value
                if max(self.slopes) < 0:
                    if self.positive_slope:
                        self.peak = True
                        self.positive_slope = False
                        self.negative_slope = False
                    else:
                        self.positive_slope = False
                        self.negative_slope = True
                elif min(self.slopes) > 0:
                    if self.negative_slope:
                        self.valley = True
                        self.positive_slope = False
                        self.negative_slope = False
                    else:
                        self.positive_slope = True
                        self.negative_slope = False

            self.slope_age = (self.slope_age + 1) % self.window

        self.age = (self.age + 1) % self.slope_window

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
