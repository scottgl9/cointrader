# Relative Strength Index (RS)
from trader.lib.struct.IndicatorBase import IndicatorBase


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
        self._last_u = 0
        self._last_d = 0
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
            self.up_values.append(0.0)
            self.down_values.append(0.0)
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
            if float(close) > self.last_close:
                u = float(close) - self.last_close
                d = 0
                self._sum_up += u
            elif float(close) < self.last_close:
                u = 0
                d = self.last_close - float(close)
                self._sum_down += d
            else:
                u = 0
                d = 0

            self._sum_up -= self.up_values[int(self.age)]
            self._sum_down -= self.down_values[int(self.age)]
            self.up_values[int(self.age)] = u
            self.down_values[int(self.age)] = d
            self.age = (self.age + 1) % self.window

            self._prev_avg_up = self._avg_up
            self._prev_avg_down = self._avg_down
            self._avg_up = self._sum_up / self.window
            self._avg_down = self._sum_down / self.window

            if not self.rs:
                rs1 = self._avg_up
                rs2 = self._avg_down
                self.rs = rs1 / rs2
            else:
                rs1 = ((self.window - 1) * self._prev_avg_up + u)
                rs2 = ((self.window - 1) * self._prev_avg_down + d)
                if rs2:
                    self.rs = rs1 / rs2
            if not rs2:
                self.result = 100.0
            else:
                result = 100.0 - (100.0 / (1.0 + self.rs))
                if self.smoother:
                    self.result = self.smoother.update(result)
                else:
                    self.result = result

        self.last_close = float(close)

        return self.result
