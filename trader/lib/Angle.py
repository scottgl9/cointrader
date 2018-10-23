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
    def __init__(self, window):
        self.window = window
        self.lag = ValueLag(window=self.window)
        self.lag_ts = ValueLag(window=self.window)
        self.result = 0
        self.counter = 0
        self.max_value_delta = 0

    def update(self, value, ts=0):
        if not self.lag.full() or not self.lag_ts.full():
            self.lag.update(value)
            self.lag_ts.update(ts)
            return self.result

        self.max_value_delta = 0.25 * self.lag.result
        value_delta = value - self.lag.result
        v1 = (self.window, self.max_value_delta)
        v2 = (self.window, value_delta)

        self.result = dotproduct(v1, v2) / (length(v1) * length(v2))

        #self.result = np.rad2deg(np.arctan2(delta_value, delta_ts))  # (180.0 / np.pi) * np.arctan(delta_y / delta_x)

        return self.result
