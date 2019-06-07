from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2
import numpy as np

class MTSCrossAngle(object):
    def __init__(self, win_secs=60, ma1=None, ma2=None):
        self.win_secs = win_secs
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.ts = 0
        self.start_ts = 0
        self.cross = MTSCrossover2(win_secs=self.win_secs)
        self.cross_up_value = 0
        self.cross_up_ts = 0
        self.last_cross_up_value = 0
        self.last_cross_up_ts = 0
        self.cross_down_value = 0
        self.cross_down_ts = 0
        self.last_cross_down_value = 0
        self.last_cross_down_ts = 0
        self.crossup = False
        self.crossdown = False

    def update(self, value=0, ma1_result=0, ma2_result=0, ts=0):
        self.ts = ts
        if ma1_result and ma2_result:
            self.ma1_result = ma1_result
            self.ma2_result = ma2_result
        else:
            self.ma1_result = self.ma1.update(value)
            self.ma2_result = self.ma2.update(value)

        self.cross.update(self.ma1_result, self.ma2_result, ts)
        if self.cross.crossup_detected():
            self.crossup = True
            self.last_cross_up_value = self.cross_up_value
            self.last_cross_up_ts = self.cross_up_ts
            self.cross_up_value = self.cross.crossup_value
            self.cross_up_ts = self.cross.crossup_ts
        elif self.cross.crossdown_detected():
            self.crossdown = True
            self.last_cross_down_value = self.cross_down_value
            self.last_cross_down_ts = self.cross_down_ts
            self.cross_down_value = self.cross.crossdown_value
            self.cross_down_ts = self.cross.crossdown_ts

    def crossup_detected(self, clear=True):
        result = self.crossup
        if clear:
            self.crossup = False
        return result

    def crossdown_detected(self, clear=True):
        result = self.crossdown
        if clear:
            self.crossdown = False
        return result

    def cross_angle(self):
        result1 = 0
        result2 = 0

        if not self.cross_down_ts and not self.cross_down_ts:
            return result1, result2
        if self.cross_up_ts > self.cross_down_ts:
            delta_ts = (self.ts - self.cross_up_ts) / (1000.0)
            pchange_ma1 = 100.0 * (self.ma1_result - self.cross_up_value) / self.cross_up_value
            pchange_ma2 = 100.0 * (self.ma2_result - self.cross_up_value) / self.cross_up_value
            result1 = pchange_ma1
            result2 = pchange_ma2
            #v0 = np.array([delta_ts, delta_ma1])
            #v1 = np.array([delta_ts, delta_ma2])
            #angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
        elif self.cross_up_ts < self.cross_down_ts:
            delta_ts = (self.ts - self.cross_down_ts) / (1000.0)
            pchange_ma1 = 100.0 * (self.ma1_result - self.cross_down_value) / self.cross_down_value
            pchange_ma2 = 100.0 * (self.ma2_result - self.cross_down_value) / self.cross_down_value
            result1 = pchange_ma1
            result2 = pchange_ma2
            #v0 = np.array([delta_ts, delta_ma1])
            #v1 = np.array([delta_ts, delta_ma2])
            #angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
        return result1, result2
