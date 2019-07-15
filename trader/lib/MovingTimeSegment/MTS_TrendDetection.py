from .MovingTimeSegment import MovingTimeSegment

class MTS_TrendDetection(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.mts = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False)
        self.last_max_high_value = 0
        self.last_max_high_ts = 0
        self.last_min_low_value = 0
        self.last_min_low_ts = 0
        self._trend_up = False
        self._trend_down = False
        self._prev_trend_up = False
        self._prev_trend_down = False

    def ready(self):
        return self.mts.ready()

    def update(self, value, ts):
        self.mts.update(value, ts)

        if not self.mts.ready():
            return

        if self.mts.max() >= self.last_max_high_value:
            self.last_max_high_value = value
            self.last_max_high_ts = ts
            self._prev_trend_up = self._trend_up
            self._prev_trend_down = self._trend_down
            self._trend_up = True
            self._trend_down = False
        if not self.last_min_low_value or self.mts.min() <= self.last_min_low_value:
            self.last_min_low_value = value
            self.last_min_low_ts = ts
            self._prev_trend_up = self._trend_up
            self._prev_trend_down = self._trend_down
            self._trend_up = False
            self._trend_down = True

        if self.last_min_low_ts and self.last_max_high_ts:
            if ((ts - self.last_max_high_ts) >= self.win_secs * 1000 or
                (ts - self.last_min_low_ts) >= self.win_secs * 1000):
                self._prev_trend_up = self._trend_up
                self._prev_trend_down = self._trend_down
                self._trend_up = False
                self._trend_down = False

    def trending_up(self):
        return self._trend_up

    def trending_down(self):
        return self._trend_down

    # reversal of upward trend
    def trend_up_reverse(self):
        if (not self._prev_trend_down and self._trend_down and
            self._prev_trend_up and not self._trend_up):
            return True
        return False

    # reversal of downward trend
    def trend_down_reverse(self):
        if (self._prev_trend_down and not self._trend_down and
            not self._prev_trend_up and self._trend_up):
            return True
        return False
