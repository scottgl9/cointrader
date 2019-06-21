from .MovingTimeSegment import MovingTimeSegment

class MTS_Slope(object):
    def __init__(self, win_secs=3600, slope_secs=300):
        self.win_secs = win_secs
        self.slope_secs = slope_secs
        self.mts = MovingTimeSegment(seconds=self.win_secs, disable_fmm=True)
        self.mts_slope = MovingTimeSegment(seconds=self.slope_secs, disable_fmm=True)
        self.result = 0

    def update(self, value, ts):
        self.mts.update(value, ts)
        if not self.mts.ready():
            return self.result
        self.mts_slope.update(self.mts.last_value() - self.mts.first_value(), ts)
        if not self.mts_slope.ready():
            return self.result
        self.result = self.mts_slope.last_value() - self.mts_slope.first_value()
        return self.result
