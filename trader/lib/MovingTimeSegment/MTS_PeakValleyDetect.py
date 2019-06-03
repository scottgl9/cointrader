# Moving Time Segment (MTS) Peak / Valley Detection
from .MovingTimeSegment import MovingTimeSegment


class MTS_PeakValleyDetect(object):
    def __init__(self, value_win_secs=60, slope_win_secs=3600):
        self.value_win_secs = value_win_secs
        self.slope_win_secs = slope_win_secs
        self.mts_values = MovingTimeSegment(seconds=self.value_win_secs, disable_fmm=True)
        self.mts_slopes = MovingTimeSegment(seconds=self.slope_win_secs, disable_fmm=False)
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

    def update(self, value, ts):
        self.mts_values.update(value, ts)
        if not self.mts_values.ready():
            return

        self.mts_slopes.update(self.mts_values.last_value() - self.mts_values.first_value(), ts)
        if not self.mts_slopes.ready():
            return

        if self.mts_slopes.max() < 0:
            if self.positive_slope:
                self.peak = True
                self.positive_slope = False
                self.negative_slope = False
            else:
                self.positive_slope = False
                self.negative_slope = True
        elif self.mts_slopes.min() > 0:
            if self.negative_slope:
                self.valley = True
                self.positive_slope = False
                self.negative_slope = False
            else:
                self.positive_slope = True
                self.negative_slope = False

    #def percent_change(self):
    #    low = min(self.values)
    #    high = max(self.values)
    #    return 100 * (high - low) / low

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
