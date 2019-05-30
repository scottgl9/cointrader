from .MovingTimeSegment import MovingTimeSegment

class MTS_RSI(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.mts_up = MovingTimeSegment(seconds=self.win_secs)
        self.mts_down = MovingTimeSegment(seconds=self.win_secs)
        self._prev_avg_up = 0
        self._prev_avg_down = 0
        self._avg_up = 0
        self._avg_down = 0
        self.rs = 0
        self.result = 0
        self.last_value = 0

    def update(self, value, ts):
        if self.last_value == 0:
            self.last_value = float(value)
            self.mts_up.update(0.0, ts)
            self.mts_down.update(0,0, ts)
            return self.result
        if not self.mts_up.ready():
            if float(value) > self.last_value:
                u = float(value) - self.last_value
                d = 0.0
            else:
                u = 0.0
                d = self.last_value - float(value)
            self.mts_up.update(u, ts)
            self.mts_down.update(d, ts)
        else:
            if float(value) > self.last_value:
                u = float(value) - self.last_value
                d = 0.0
            elif float(value) < self.last_value:
                u = 0.0
                d = self.last_value - float(value)
            else:
                u = 0.0
                d = 0.0

            self.mts_up.update(u, ts)
            self.mts_down.update(d, ts)

            self._prev_avg_up = self._avg_up
            self._prev_avg_down = self._avg_down
            self._avg_up = self.mts_up.get_sum() / self.mts_up.get_sum_count()
            self._avg_down = self.mts_down.get_sum() / self.mts_down.get_sum_count()

            if not self.rs:
                rs1 = self._avg_up
                rs2 = self._avg_down
                self.rs = rs1 / rs2
            else:
                rs1 = ((self.mts_up.get_sum_count() - 1) * self._prev_avg_up + u)
                rs2 = ((self.mts_up.get_sum_count() - 1) * self._prev_avg_down + d)
                if rs2:
                    self.rs = rs1 / rs2
            if not rs2:
                self.result = 100.0
            else:
                self.result = 100.0 - (100.0 / (1.0 + self.rs))

        self.last_value = float(value)

        return self.result
