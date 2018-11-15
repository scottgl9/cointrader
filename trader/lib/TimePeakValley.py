# determine how much time has passed since a new high, or a new low value. If that time is greater
# than specified number of seconds, mark as peak or valley respectively

# The logic of TimePeakValley works as follows:
# 1) For the case where price is trending up, then hits a peak and reverses direction:
# - max_value set to value, min_value set to value, max_value_ts set to ts, min_value_ts set to ts
# - value is increasing, so max_value and max_value_ts are updated each time there is a new higher value,
#   and min_value, min_value_ts stay the same
# - last_max_value_ts and last_min_value_ts are updated to max_value_ts and min_value_ts on update respectively
# - also last_max_value and last_min_value are updated to max_value and min_value on update respectively
# - If time since max_value was set is > self.seconds and value < min_value and
#   (ts - last_min_value_ts) > self.seconds and (ts - last_min_value_ts) > (ts - last_max_value_ts): then
#   mark as peak

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
        self.last_max_value = 0
        self.max_value_ts = 0
        self.last_max_value_ts = 0
        self.min_value = 0
        self.last_min_value = 0
        self.min_value_ts = 0
        self.last_min_value_ts = 0

    def update(self, value, ts):
        if self.max_value == 0:
            self.max_value = value
            self.max_value_ts = ts
        elif value > self.max_value:
            self.last_max_value = self.max_value
            self.max_value = value
            self.last_max_value_ts = self.max_value_ts
            self.max_value_ts = ts

        if self.min_value == 0:
            self.min_value = value
            self.min_value_ts = ts
        elif value < self.min_value:
            self.last_min_value = self.min_value
            self.min_value = value
            self.last_min_value_ts = self.min_value_ts
            self.min_value_ts = ts

        if not self.peak and self.min_value_ts != 0 and (ts - self.min_value_ts) > self.seconds * 1000:
            self.valley = True
        elif not self.valley and self.max_value_ts != 0 and (ts - self.max_value_ts) > self.seconds * 1000:
            self.peak = True