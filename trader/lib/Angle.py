import numpy as np
import math
from trader.lib.ValueLag import ValueLag
from trader.lib.TimeSegmentValues import TimeSegmentValues

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.degrees(math.acos(dotproduct(v1, v2) / (length(v1) * length(v2))))

class Angle(object):
    def __init__(self, seconds):
        self.tsv1 = TimeSegmentValues(seconds)
        self.tsv2 = TimeSegmentValues(seconds)
        self.result = 0
        self.counter = 0

    def update(self, value1, value2, ts=0):
        self.tsv1.update(float(value1), ts)
        self.tsv2.update(float(value2), ts)

        if not self.tsv1.ready() or not self.tsv1.ready():
            return self.result

        side1_len = np.sqrt(self.tsv1.value_count()**2 + self.tsv1.diff()**2)
        side2_len = np.sqrt(self.tsv2.value_count()**2 + self.tsv2.diff()**2)
        self.result = side1_len / side2_len

        #v1 = (self.tsv1.diff_ts()/1000, value1_delta)
        #v2 = (self.tsv1.diff_ts()/1000, value2_delta)
        #self.result = dotproduct(v1, v2) / (length(v1) * length(v2))

        #self.result = np.rad2deg(np.arctan2(delta_value, delta_ts))  # (180.0 / np.pi) * np.arctan(delta_y / delta_x)

        return self.result

    def detrend_result(self):
        if not self.tsv1.ready() or not self.tsv2.ready():
            return 0

        result = (self.tsv1.diff() - self.tsv2.diff())
        return result
