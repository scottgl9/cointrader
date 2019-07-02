from .MovingTimeSegment import MovingTimeSegment
from .MTSCrossover2 import MTSCrossover2


class MTS_Retracement(object):
    def __init__(self, win_secs=3600, short_smoother=None, long_smoother=None):
        self.win_secs = win_secs
        self.tracker1 = MTS_Track(win_secs=win_secs, smoother=short_smoother)

    def update(self, value, ts):
        self.tracker1.update(value, ts)

    def crossup_detected(self, clear=True):
        return self.tracker1.crossup_detected(clear=clear)

    def crossdown_detected(self, clear=True):
        return self.tracker1.crossdown_detected(clear=clear)

    def crossdown2_detected(self, clear=True):
        return self.tracker1.crossdown2_detected(clear=clear)

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
        self._mts1_slope = 0
        self._mts2_slope = 0
        self._mts3_slope = 0
        self._mts1_avg = 0
        self._mts2_avg = 0
        self.cross_up = MTSCrossover2(win_secs=60)
        self.cross_down = MTSCrossover2(win_secs=60)
        self.cross_down2 =  MTSCrossover2(win_secs=60)
        self.result = 0
        self._prev_crossup = False
        self._prev_crossdown = False
        self._crossup = False
        self._crossdown = False
        self._crossdown2 = False
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

        self.cross_up.update(self.mts1.last_value(), self.mts2.max(), ts)
        self.cross_down.update(self.mts1.last_value(), self.mts2.min(), ts)

        self._mts1_slope = self.mts1.last_value() - self.mts1.first_value()
        self._mts2_slope = self.mts2.last_value() - self.mts2.first_value()
        self._mts1_avg = self.mts1.get_sum() / self.mts1.get_sum_count()
        self._mts2_avg = self.mts2.get_sum() / self.mts2.get_sum_count()

        if  self.cross_up.crossup_detected():
            self._prev_crossup = self._crossup
            self._prev_crossdown = self._crossdown
            self._crossup = True
            self._crossdown = False
            self._crossup_ts = ts
            self._crossup_value = self.mts1.last_value()

        if self.cross_down.crossdown_detected():
            self._prev_crossup = self._crossup
            self._prev_crossdown = self._crossdown
            self._crossup = False
            self._crossdown = True
            self._crossdown_ts = ts
            self._crossdown_value = self.mts1.last_value()

        self.mts3.update(self.mts2.first_value(), ts)
        if not self.mts3.ready():
            return self.result

        self._mts3_slope = self.mts3.last_value() - self.mts3.first_value()
        self.cross_down2.update(self.mts1.last_value(), self.mts3.min(), ts)
        if self.cross_down2.crossdown_detected():
            self._crossup = False
            self._crossdown2 = True

    def crossup_detected(self, clear=True):
        result = self._crossup
        if clear:
            self._crossup = False
        return result

    def crossdown_detected(self, clear=True):
        result = self._crossdown
        if clear:
            self._crossdown = False
        return result

    def crossdown2_detected(self, clear=True):
        result = self._crossdown2
        if clear:
            self._crossdown2 = False
        return result

    def mts1_avg(self):
        return self._mts1_avg

    def mts2_avg(self):
        return self._mts2_avg
