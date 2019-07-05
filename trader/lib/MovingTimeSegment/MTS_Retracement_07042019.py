from trader.indicator.EMA import EMA
from .MovingTimeSegment import MovingTimeSegment
from .MTSCrossover2 import MTSCrossover2


class MTS_Retracement(object):
    def __init__(self, win_secs=3600, short_smoother=None, long_smoother=None):
        self.win_secs = win_secs
        self.tracker1 = MTS_Track(win_secs=win_secs, smoother=short_smoother)
        self.tracker2 = MTS_Track(win_secs=win_secs, smoother=long_smoother)

    def hourly_load(self, start_ts=0, end_ts=0, ts=0):
        pass

    def hourly_update(self, hourly_ts):
        pass

    def update(self, value, ts):
        self.tracker1.update(value, ts)
        self.tracker2.update(value, ts)

    def get_short_mts1(self):
        return self.tracker1.mts1

    def get_short_mts2(self):
        return self.tracker1.mts2

    def get_long_mts1(self):
        return self.tracker1.mts1

    def get_long_mts2(self):
        return self.tracker1.mts2

    def crossup_detected(self, clear=True):
        if self.tracker1.mts1_slope < 0 and self.tracker1.mts2_slope < 0:
            return False
        if (self.tracker1.mts1.max() <= self.tracker1.mts2.max() or
            self.tracker1.mts1.min() <= self.tracker1.mts2.min()):
            return False
        return self.tracker1.cross_up_mts2_up_detected(clear=clear)

    def crossdown_detected(self, clear=True):
        if self.tracker1.cross_down_mts2_down_detected(clear=clear):
            return True
        return False

    def crossdown2_detected(self, clear=True):
        return self.tracker1.cross_down_mts3_down_detected(clear=clear)

    def long_crossdown_detected(self, clear=True):
        if (self.tracker2.mts1.max() >= self.tracker2.mts2.max() or
            self.tracker2.mts1.min() >= self.tracker2.mts2.min()):
            return False
        if self.tracker2.mts1_slope < 0 and self.tracker2.mts2_slope < 0:
            return self.tracker2.cross_down_mts3_down_detected(clear=clear)
        return False

    def mts1_avg(self):
        return self.tracker1.mts1_avg()

    def mts2_avg(self):
        return self.tracker1.mts2_avg()


class MTS_Track(object):
    def __init__(self, win_secs, smoother=None):
        self.win_secs = win_secs
        self.smoother = smoother
        self.mts1 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)
        self.mts2 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)
        self.mts3 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=False)

        self.mts1_slope = 0
        self.mts2_slope = 0
        self.mts3_slope = 0
        self._mts1_avg = 0
        self._mts2_avg = 0
        self.cross_up_mts2 = MTSCrossover2(win_secs=60)
        self.cross_down_mts2 = MTSCrossover2(win_secs=60)
        self.cross_up_mts3 = MTSCrossover2(win_secs=60)
        self.cross_down_mts3 =  MTSCrossover2(win_secs=60)
        self.result = 0
        self._cross_up_mts2_up = False
        self._cross_up_mts2_down = False
        self._cross_down_mts2_up = False
        self._cross_down_mts2_down = False
        self._cross_up_mts3_up = False
        self._cross_up_mts3_down = False
        self._cross_down_mts3_up = False
        self._cross_down_mts3_down = False
        self._crossup_value = 0
        self._crossdown_value = 0
        self._crossup_ts = 0
        self._crossdown_ts = 0

    def update(self, value, ts):
        result = value
        if self.smoother:
            result = self.smoother.update(value, ts)

        self.mts1.update(result, ts)
        if not self.mts1.ready():
            return self.result

        self.mts1.get_sum()

        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return self.result

        self.cross_up_mts2.update(self.mts1.last_value(), self.mts2.max(), ts)
        self.cross_down_mts2.update(self.mts1.last_value(), self.mts2.min(), ts)

        self.mts1_slope = self.mts1.diff()
        self.mts2_slope = self.mts2.diff()
        self._mts1_avg = self.mts1.get_sum() / self.mts1.get_sum_count()
        self._mts2_avg = self.mts2.get_sum() / self.mts2.get_sum_count()

        if  self.cross_up_mts2.crossup_detected():
            self._cross_up_mts2_up = True
            self._cross_down_mts2_down = False
            self._crossup_ts = ts
            self._crossup_value = self.mts1.last_value()
        elif self.cross_up_mts2.crossdown_detected():
            self._cross_up_mts2_down = True

        if self.cross_down_mts2.crossdown_detected():
            self._cross_up_mts2_up = False
            self._cross_down_mts2_down = True
            self._crossdown_ts = ts
            self._crossdown_value = self.mts1.last_value()
        elif self.cross_down_mts2.crossup_detected():
            self._cross_down_mts2_up = True

        self.mts3.update(self.mts2.first_value(), ts)
        if not self.mts3.ready():
            return self.result

        self.mts3_slope = self.mts3.diff()
        self.cross_down_mts3.update(self.mts1.last_value(), self.mts3.min(), ts)
        self.cross_up_mts3.update(self.mts1.last_value(), self.mts3.min(), ts)

        if self.cross_up_mts3.crossup_detected():
            self._cross_up_mts3_up = True
        elif self.cross_up_mts3.crossdown_detected():
            self._cross_up_mts3_down = True

        if self.cross_down_mts3.crossdown_detected():
            self._cross_down_mts3_down = True
        elif self.cross_down_mts3.crossup_detected():
            self._cross_down_mts3_up = True

    def cross_up_mts2_up_detected(self, clear=True):
        result = self._cross_up_mts2_up
        if clear:
            self._cross_up_mts2_up = False
        return result

    def cross_up_mts2_down_detected(self, clear=True):
        result = self._cross_up_mts2_down
        if clear:
            self._cross_up_mts2_down = False
        return result

    def cross_down_mts2_down_detected(self, clear=True):
        result = self._cross_down_mts2_down
        if clear:
            self._cross_down_mts2_down = False
        return result

    def cross_down_mts3_down_detected(self, clear=True):
        result = self._cross_down_mts3_down
        if clear:
            self._cross_down_mts3_down = False
        return result

    def mts1_avg(self):
        return self._mts1_avg

    def mts2_avg(self):
        return self._mts2_avg
