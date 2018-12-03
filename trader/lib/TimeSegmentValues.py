# Given a specified time segment, only keep track of newest values no older than the set time segment


class TimeSegmentValues(object):
    def __init__(self, seconds=0, minutes=0, value_smoother=None, percent_smoother=None):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += minutes * 60
        self.seconds_ts = 1000 * self.seconds
        self.values = []
        self.timestamps = []
        self.full = False
        self.value_smoother = value_smoother
        self.percent_smoother = percent_smoother

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
            self.values.append(value)
            self.timestamps.append(ts)

        cnt = 0
        while (ts - self.timestamps[cnt]) > self.seconds_ts:
            cnt += 1

        if cnt != 0:
            self.timestamps = self.timestamps[cnt:]
            self.values = self.values[cnt:]
            if not self.full:
                self.full = True

    def min(self):
        return min(self.values)

    def max(self):
        return max(self.values)

    def get_values(self):
        return self.values

    def value_count(self):
        return len(self.values)

    def first_value(self):
        if self.empty():
            return 0
        return self.values[0]

    def last_value(self):
        if self.empty():
            return 0
        return self.values[-1]

    def diff(self):
        if self.empty():
            return 0
        return self.values[-1] - self.values[0]

    def percent_change(self):
        if self.empty():
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
