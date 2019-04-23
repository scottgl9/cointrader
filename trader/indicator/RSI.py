# Relative Strength Index (RS)
from .IndicatorBase import IndicatorBase


class RSI(IndicatorBase):
    def __init__(self, window=14, smoother=None):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window

        self._sum_up = 0
        self._sum_down = 0
        self._prev_avg_up = 0
        self._prev_avg_down = 0
        self._avg_up = 0
        self._avg_down = 0
        self.up_values = []
        self.down_values = []
        self.age = 0
        self.last_close = 0
        self.rs = 0
        self.result = 0
        self.smoother = smoother

    def update(self, close):
        if self.last_close == 0:
            self.last_close = float(close)
            return self.result

        if len(self.up_values) < self.window:
            if float(close) > self.last_close:
                u = float(close) - self.last_close
                d = 0.0
                self._sum_up += u
            else:
                u = 0.0
                d = self.last_close - float(close)
                self._sum_down += d
            self.up_values.append(u)
            self.down_values.append(d)
        else:
            self._sum_up -= self.up_values[int(self.age)]
            self._sum_down -= self.down_values[int(self.age)]

            if float(close) > self.last_close:
                u = float(close) - self.last_close
                d = 0.0
                self._sum_up += u
            else:
                u = 0.0
                d = self.last_close - float(close)
                self._sum_down += d

            self.up_values[int(self.age)] = u
            self.down_values[int(self.age)] = d
            self._prev_avg_up = self._avg_up
            self._avg_up = self._sum_up / self.window
            self._prev_avg_down = self._avg_down
            self._avg_down = self._sum_down / self.window
            if not self.rs:
                self.rs = self._avg_up / self._avg_down
            else:
                rs1 = ((self.window - 1) * self._prev_avg_up + u)
                rs2 = ((self.window - 1) * self._prev_avg_down + d)
                self.rs = rs1 / rs2
            self.result = 100.0 - (100.0 / (1.0 + self.rs))
            self.age = (self.age + 1) % self.window

        self.last_close = float(close)

        return self.result
