import numpy as np
import math
from trader.lib.ValueLag import ValueLag

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))

class Angle(object):
    def __init__(self, window, min_value=0, max_value=0, max_window=0):
        self.window = window
        self.lag = ValueLag(window=self.window)
        self.lag_ts = ValueLag(window=self.window)
        self.result = 0
        self.counter = 0
        self.max_value = max_value
        self.min_value = min_value
        self.max_window = max_window

    def update(self, value, ts=0):
        if self.min_value == 0 or self.max_value == 0:
            self.min_value = 0.95 * value
            self.max_value = 1.05 * value

        if self.max_window == 0:
            self.max_window = 15000

        if value < self.min_value:
            self.min_value = value
        elif value > self.max_value:
            self.max_value = value

        if not self.lag.full() or not self.lag_ts.full():
            self.lag.update(value)
            self.lag_ts.update(ts)
            return self.result

        if int(self.lag_ts.result) == ts or self.lag_ts.result == 0:
            self.lag.update(value)
            self.lag_ts.update(ts)
            return self.result

        delta_ts = float(self.window) / self.max_window
        delta_value = (value - self.lag.result) / (self.max_value - self.min_value)
        #hyp = np.sqrt(delta_ts * delta_ts + delta_value * delta_value)

        #v1 = (delta_ts, 0)
        #v2 = (delta_ts, delta_value)

        self.lag.update(value)
        self.lag_ts.update(ts)

        self.result = np.rad2deg(np.arctan2(delta_value, delta_ts))  # (180.0 / np.pi) * np.arctan(delta_y / delta_x)

        return self.result