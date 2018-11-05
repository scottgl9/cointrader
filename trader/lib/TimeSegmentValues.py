# Given a specified time segment, only keep track of newest values no older than the set time segment

class TimeSegmentValues(object):
    def __init__(self, seconds):
        self.seconds = seconds
        self.time_values = []
        self.full = False

    def empty(self):
        if len(self.time_values) == 0:
            return True
        return False

    def update(self, value, ts):
        self.time_values.append(TimeValue(value, ts))

        while (ts - self.time_values[0].ts) > 1000 * self.seconds:
            self.time_values = self.time_values[1:]
            if not self.full:
                self.full = True

    def get_values(self):
        values = []
        for tv in self.time_values:
            values.append(tv.value)
        return values

    def get_first_value(self):
        if self.empty():
            return 0

        return self.time_values[0].value

    def get_last_value(self):
        if self.empty():
            return 0

        return self.time_values[-1].value

class TimeValue(object):
    def __init__(self, value=0, ts=0):
        self.value = value
        self.ts = ts
