# determine how much time has passed since a new high, or a new low value. If that time is greater
# than specified number of seconds, mark as peak or valley respectively

class TimePeakValley(object):
    def __init__(self, seconds):
        self.max_value = 0
        self.max_value_ts = 0
        self.min_value = 0
        self.min_value_ts = 0
        self.seconds = seconds
        self.peak = False
        self.valley = False

    def peak_detected(self, clear=False):
        result = self.peak
        if clear:
            self.peak = False
            self.reset()
        return result

    def valley_detected(self, clear=False):
        result = self.valley
        if clear:
            self.valley = False
            self.reset()
        return result

    def reset(self):
        self.valley = False
        self.peak = False
        self.max_value = 0
        self.max_value_ts = 0
        self.min_value = 0
        self.min_value_ts = 0

    def update(self, value, ts):
        if self.max_value == 0 or self.min_value == 0:
            self.max_value = value
            self.min_value = value
            self.max_value_ts = ts
            self.min_value_ts = ts
        elif value > self.max_value:
            self.max_value = value
            self.max_value_ts = ts
        elif value < self.min_value:
            self.min_value = value
            self.min_value_ts = ts

        if not self.valley and self.min_value_ts != 0 and (ts - self.min_value_ts) > self.seconds * 1000:
            self.valley = True
        elif not self.peak and self.max_value_ts != 0 and (ts - self.max_value_ts) > self.seconds * 1000:
            self.peak = True
