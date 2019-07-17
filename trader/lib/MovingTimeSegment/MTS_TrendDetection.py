from .MovingTimeSegment import MovingTimeSegment

class MTS_TrendDetection(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.mts1 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False)
        self.mts2 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False)
        self._mts1_gt_mts2_start_ts = 0
        self._mts1_lt_mts2_start_ts = 0
        self._uptrend_started = False
        self._downtrend_started = False

    def ready(self):
        return self.mts2.ready()

    def update(self, value, ts):
        self.mts1.update(value, ts)

        if not self.mts1.ready():
            return

        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return

        if self.mts1.max() > self.mts2.max() and self.mts1.min() > self.mts2.min():
            if not self._mts1_gt_mts2_start_ts:
                self._mts1_gt_mts2_start_ts = ts
            self._mts1_lt_mts2_start_ts = 0
        elif self.mts1.max() < self.mts2.max() and self.mts1.min() < self.mts2.min():
            if not self._mts1_lt_mts2_start_ts:
                self._mts1_lt_mts2_start_ts = ts
            self._mts1_gt_mts2_start_ts = 0
        #elif self.mts1.max() == self.mts2.max() or self.mts1.min() == self.mts2.min():
        #    pass
        else:
            self._mts1_gt_mts2_start_ts = 0
            self._mts1_lt_mts2_start_ts = 0

        if  self._mts1_gt_mts2_start_ts and ts - self._mts1_gt_mts2_start_ts > self.win_secs * 1000:
            self._uptrend_started = True
            self._downtrend_started = False
            self._mts1_gt_mts2_start_ts = 0
        elif self._mts1_lt_mts2_start_ts and ts - self._mts1_lt_mts2_start_ts > self.win_secs * 1000:
            self._uptrend_started = False
            self._downtrend_started = True
            self._mts1_lt_mts2_start_ts = 0
    def uptrend_started(self, clear=True):
        result = self._uptrend_started
        if clear:
            self._uptrend_started = False
        return result

    def downtrend_started(self, clear=True):
        result = self._downtrend_started
        if clear:
            self._downtrend_started = False
        return result
