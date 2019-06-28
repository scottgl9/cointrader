from .MovingTimeSegment import MovingTimeSegment
from .MTSCrossover2 import MTSCrossover2


class MTS_Retracement(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.mts1 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False)
        self.mts2 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False)
        self.cross_up = MTSCrossover2(win_secs=60)
        self.cross_down = MTSCrossover2(win_secs=60)
        self.result = 0
        self.prev_trend_up = False
        self.prev_trend_down = False
        self.trend_up = False
        self.trend_down = False

    def update(self, value, ts):
        self.mts1.update(value, ts)
        if not self.mts1.ready():
            return self.result

        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return self.result

        self.cross_up.update(self.mts2.last_value(), self.mts1.max(), ts)
        self.cross_down.update(self.mts2.last_value(), self.mts1.min(), ts)

        if self.cross_up.crossup_detected():
            self.prev_trend_up = self.trend_up
            self.prev_trend_down = self.trend_down
            self.trend_up = True
            self.trend_down = False

        if self.cross_down.crossdown_detected():
            self.prev_trend_up = self.trend_up
            self.prev_trend_down = self.trend_down
            self.trend_up = False
            self.trend_down = True

    def crossup_detected(self, clear=False):
        result = self.trend_up
        if clear:
            self.trend_up = False
        return result

    def crossdown_detected(self, clear=False):
        result = self.trend_down
        if clear:
            self.trend_down = False
        return result
