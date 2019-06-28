# more efficient way to calculate min(values) and max(values) by tracking the maximum and minimums, versus
# just calling min(values) or max(values) for every change in values


# allows for a variable size of values, when values can be removed, but always keeps track of min and max values
class FastMinMax(object):
    def __init__(self, track_ts=False):
        self.track_ts = track_ts
        self.values = []
        self.timestamps = []
        self.min_value = 0
        self.min_value_index = -1
        self.min_value_ts = 0
        self.max_value = 0
        self.max_value_index = -1
        self.max_value_ts = 0
        self.end_index = 0

    def min(self):
        return self.min_value

    def max(self):
        return self.max_value

    def min_ts(self):
        return self.min_value_ts

    def max_ts(self):
        return self.max_value_ts

    def append(self, value, ts=0):
        if self.min_value == 0 or self.max_value == 0:
            self.min_value = value
            self.min_value_index = 0
            self.max_value = value
            self.max_value_index = 0
            if self.track_ts:
                self.min_value_ts = ts
                self.max_value_ts = ts
                self.timestamps.append(ts)
            self.values.append(value)
            return

        if self.min_value != 0 and value < self.min_value:
            self.min_value = value
            self.min_value_index = self.end_index
            self.min_value_ts = ts
        elif value > self.max_value:
            self.max_value = value
            self.max_value_index = self.end_index
            self.max_value_ts = ts

        if self.track_ts:
            self.timestamps.append(ts)

        self.values.append(value)
        self.end_index += 1

    # remove count items from beginning of self.values
    def remove(self, count):
        if len(self.values) <= count:
            return
        self.min_value_index -= count
        self.max_value_index -= count
        self.end_index -= count

        self.values = self.values[count:]

        if self.track_ts:
            self.timestamps = self.timestamps[count:]

        if self.min_value_index < 0:
            self.min_value_index = min(xrange(len(self.values)), key=self.values.__getitem__)

        self.min_value = self.values[self.min_value_index]

        if self.max_value_index < 0:
            self.max_value_index = max(xrange(len(self.values)), key=self.values.__getitem__)

        self.max_value = self.values[self.max_value_index]

        if self.track_ts:
            self.min_value_ts = self.timestamps[self.min_value_index]
            self.max_value_ts = self.timestamps[self.max_value_index]
