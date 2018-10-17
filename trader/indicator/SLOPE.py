# simple moving slope indicator
class SLOPE(object):
    def __init__(self, window=50, use_timestamps=False):
        self.window = window
        self.use_timestamps = use_timestamps
        self.values = []
        self.timestamps = []
        self.age = 0
        self.result = 0

    def update(self, value, ts=0):
        if len(self.values) < self.window:
            self.values.append(float(value))
            if self.use_timestamps:
                self.timestamps.append(ts / 1000.0)
        else:
            old_value = self.values[int(self.age)]
            self.values[int(self.age)] = float(value)

            if self.use_timestamps:
                old_ts = self.timestamps[int(self.age)]
                self.timestamps[int(self.age)] = ts / 1000.0
                self.result = (float(value) - old_value) / (ts - old_ts)
            else:
                self.result = (float(value) - old_value) / self.window

        self.age = (self.age + 1) % self.window

        return self.result
