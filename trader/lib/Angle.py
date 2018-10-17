import numpy as np
from trader.lib.ValueLag import ValueLag

class Angle(object):
    def __init__(self, window):
        self.window = window
        self.lag = ValueLag(window=self.window)
        self.lag_ts = ValueLag(window=self.window)
        self.result = 0

    def update(self, value, ts=0):
        if not self.lag.full():
            self.lag.update(value)
            self.lag_ts.update(ts/1000.0)
            return self.result

        if int(self.lag_ts.result) == int(ts/1000.0) or self.lag_ts.result == 0:
            self.lag.update(value)
            self.lag_ts.update(ts/1000.0)
            return self.result

        self.result = self.lag.result #(180.0 / np.pi) * np.arcsin(delta_y / hyp)

        self.lag.update(value)
        self.lag_ts.update(ts)

        return self.result
