from .MovingTimeSegment import MovingTimeSegment
from .MTSCrossover2 import MTSCrossover2


class MTS_Retracement(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.mts1 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=True)
        self.mts2 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=True)
        self.mts3 = MovingTimeSegment(seconds=self.win_secs, disable_fmm=False, track_ts=True)
        self.cross_up = MTSCrossover2(win_secs=60)
        self.cross_down = MTSCrossover2(win_secs=60)
        self.long_cross_down =  MTSCrossover2(win_secs=60)
        self.result = 0
        self._prev_crossup = False
        self._prev_crossdown = False
        self._crossup = False
        self._crossdown = False
        self._long_crossdown = False
        self._crossup_value = 0
        self._crossdown_value = 0
        self._long_crossdown_value = 0
        self._crossup_ts = 0
        self._crossdown_ts = 0
        self._long_crossdown_ts = 0

    def update(self, value, ts):
        self.mts1.update(value, ts)
        if not self.mts1.ready():
            return self.result

        self.mts2.update(self.mts1.first_value(), ts)
        if not self.mts2.ready():
            return self.result

        self.cross_up.update(self.mts1.last_value(), self.mts2.max(), ts)
        self.cross_down.update(self.mts1.last_value(), self.mts2.min(), ts)

        #self.cross.update(self.mts1.last_value(), self.mts2.first_value(), ts)
        #self.cross_down.update(self.mts1.last_value(), self.mts2.first_value(), ts)

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
        if self.mts3.ready():
            self.long_cross_down.update(self.mts1.last_value(), self.mts3.min(), ts)
            if self.long_cross_down.crossdown_detected():
                self._crossup = False
                self._long_crossdown = True
                self._long_crossdown_ts = ts
                self._long_crossdown_value = self.mts1.last_value()

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

    def long_crossdown_detected(self, clear=True):
        result = self._long_crossdown
        if clear:
            self._long_crossdown = False
        return result
