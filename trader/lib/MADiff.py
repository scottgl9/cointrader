# indicator which tracks the current distance between two MAs
from trader.lib.Crossover2 import Crossover2


class MADiff(object):
    def __init__(self, ma1=None, ma2=None):
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.result = 0
        self._ready = False
        self.max_diff = 0
        self.max_diff_ts = 0
        self.cross_diff_zero = Crossover2(window=10)
        self.cross_up = False
        self.cross_up_ts = 0
        self.cross_down = False
        self.cross_down_ts = 0

    def ready(self):
        return self._ready

    def update(self, value, ts, ma1_result=0, ma2_result=0):
        if self.ma1:
            self.ma1.update(value)
            self.ma1_result = self.ma1.result
        else:
            self.ma1_result = ma1_result

        if self.ma2:
            self.ma2.update(value)
            self.ma2_result = self.ma2.result
        else:
            self.ma2_result = ma2_result

        # update maximum diff after latest crossover (up or down)
        if self.ma1_result and self.ma2_result:
            self.result = self.ma1_result - self.ma2_result
            self._ready = True
            if self.cross_up and self.result > self.max_diff:
                self.max_diff = self.result
                self.max_diff_ts = ts
            elif self.cross_down and abs(self.result) > abs(self.max_diff):
                self.max_diff = self.result
                self.max_diff_ts = ts

        if self._ready:
            self.cross_diff_zero.update(self.result, 0)
            if self.cross_diff_zero.crossup_detected():
                self.max_diff = 0
                self.max_diff_ts = 0
                self.cross_up = True
                self.cross_down = False
                self.cross_up_ts = ts
            elif self.cross_diff_zero.crossdown_detected():
                # reset max diff
                self.max_diff = 0
                self.max_diff_ts = 0
                self.cross_up = False
                self.cross_down = True
                self.cross_down_ts = ts

        return self.result

    def get_diff(self):
        return self.result

    def get_diff_max(self):
        return self.max_diff

    def is_near_current_max(self, cutoff=0.01, percent=0.5):
        if not self._ready or self.max_diff == 0 or self.result == 0:
            return False

        if self.cross_up_ts == 0 or self.cross_down_ts > self.cross_up_ts:
            return False

        if abs((self.ma1_result - self.ma2_result) / self.ma2_result) < cutoff:
            return False

        if abs(100.0 * (self.result - self.max_diff) / self.max_diff) <= percent:
            return True
        return False
