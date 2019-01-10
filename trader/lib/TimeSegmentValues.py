# Given a specified time segment, only keep track of newest values no older than the set time segment
from trader.lib.FastMinMax import FastMinMax


class TimeSegmentValues(object):
    def __init__(self, seconds=0, minutes=0, value_smoother=None, percent_smoother=None):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += minutes * 60
        self.seconds_ts = 1000 * self.seconds
        self.values = []
        self.timestamps = []
        self.fmm = FastMinMax()
        self.full = False
        self.value_smoother = value_smoother
        self.percent_smoother = percent_smoother
        self.min_value = 0
        self.min_value_index = -1
        self.max_value = 0
        self.max_value_index = -1

    def empty(self):
        if len(self.values) == 0:
            return True
        return False

    def ready(self):
        return self.full

    def update(self, value, ts):
        if self.value_smoother:
            svalue = self.value_smoother.update(value)
            self.values.append(svalue)
            self.timestamps.append(ts)
        else:
            svalue = value
            self.values.append(svalue)
            self.timestamps.append(ts)

        cnt = 0
        while (ts - self.timestamps[cnt]) > self.seconds_ts:
            cnt += 1

        self.fmm.append(svalue)

        if cnt != 0:
            self.fmm.remove(cnt)
            self.timestamps = self.timestamps[cnt:]
            self.values = self.values[cnt:]
            if not self.full:
                self.full = True

        self.min_value = self.fmm.min()
        self.max_value = self.fmm.max()

    def min(self):
        if not self.ready():
            return 0
        #return min(self.values)
        return self.min_value

    def max(self):
        if not self.ready():
            return 0
        #return max(self.values)
        return self.max_value

    def get_values(self):
        return self.values

    def get_timestamps(self):
        return self.timestamps

    def value_count(self):
        return len(self.values)

    def first_value(self):
        if not self.ready():
            return 0
        return self.values[0]

    def last_value(self):
        if not self.ready():
            return 0
        return self.values[-1]

    def diff(self):
        if not self.ready():
            return 0
        return self.values[-1] - self.values[0]

    def diff_ts(self):
        if not self.ready():
            return 0
        return self.timestamps[-1] - self.timestamps[0]

    def percent_change(self):
        if not self.ready():
            return None
        value1 = self.first_value()
        value2 = self.last_value()
        if value1 == value2 or value1 == 0:
            return None

        if self.percent_smoother:
            result = self.percent_smoother.update(100.0 * (value2 - value1) / value1)
        else:
            result = 100.0 * (value2 - value1) / value1

        return result
