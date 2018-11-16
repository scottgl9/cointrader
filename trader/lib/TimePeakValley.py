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
    def __init__(self, reverse_secs, span_secs, cutoff=0.01):
        # reverse secs is time since last high (for peak), or last loww (for valley)
        self.reverse_seconds = reverse_secs
        # span_secs is time since low (for peak), or  high (for valley)
        self.span_seconds = span_secs
        self.cutoff = cutoff
        self.valley = False
        self.peak = False
        self.last_peak_value = 0
        self.last_valley_value = 0
        self.max_value = 0
        self.last_max_value = 0
        self.max_value_change_count = 0
        self.new_max_value = 0
        self.max_value_ts = 0
        self.last_max_value_ts = 0

        self.min_value = 0
        self.last_min_value = 0
        self.min_value_change_count = 0
        self.new_min_value = 0
        self.min_value_ts = 0
        self.last_min_value_ts = 0

    def peak_detected(self, clear=True):
        result = self.peak
        if clear:
            self.peak = False
            #self.reset()
        return result

    def valley_detected(self, clear=True):
        result = self.valley
        if clear:
            self.valley = False
            #self.reset()
        return result

    def reset(self):
        self.valley = False
        self.peak = False
        self.max_value = 0
        self.max_value_change_count = 0
        self.last_max_value = 0
        self.max_value_ts = 0
        self.last_max_value_ts = 0

        self.min_value = 0
        self.last_min_value = 0
        self.min_value_change_count = 0
        self.min_value_ts = 0
        self.last_min_value_ts = 0

    # check if delta ts > set time interval in seconds
    def delta_ts_gt_reverse_secs(self, old_ts, ts):
        if old_ts == 0 or ts == 0:
            return False
        if (ts - old_ts) > self.reverse_seconds * 1000:
            return True
        return False

    def delta_ts_gt_span_secs(self, old_ts, ts):
        if old_ts == 0 or ts == 0:
            return False
        if (ts - old_ts) > self.span_seconds * 1000:
            return True
        return False

    def update(self, value, ts):
        # initially set max_value to value, and max_value_ts to ts, and if value is greater than
        # max_value, set new max_value and max_value_ts to ts
        if self.max_value == 0:
            self.max_value = value
            self.max_value_ts = ts
        elif value > self.max_value:
            self.max_value_change_count += 1
            self.last_max_value = self.max_value
            self.max_value = value
            self.last_max_value_ts = self.max_value_ts
            self.max_value_ts = ts

        # initially set min_value to value, and min_value_ts to ts, and if value is less than
        # min_value, set new min_value and min_value_ts to ts
        if self.min_value == 0:
            self.min_value = value
            self.min_value_ts = ts
        elif value < self.min_value:
            self.min_value_change_count += 1
            self.last_min_value = self.min_value
            self.min_value = value
            self.last_min_value_ts = self.min_value_ts
            self.min_value_ts = ts

        if not self.valley and self.delta_ts_gt_span_secs(self.min_value_ts, ts) and self.delta_ts_gt_reverse_secs(self.max_value_ts, ts):
            #if abs(self.max_value - value) / self.max_value > self.cutoff:
            self.peak = True
            self.min_value = value
            self.min_value_ts = ts
        elif not self.peak and self.delta_ts_gt_span_secs(self.max_value_ts, ts) and self.delta_ts_gt_reverse_secs(self.min_value_ts, ts):
            #if abs(value - self.min_value) / self.min_value > self.cutoff:
            self.valley = True
            self.max_value = value
            self.max_value_ts = ts
