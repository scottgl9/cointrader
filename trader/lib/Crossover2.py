# crossover detection version 2
# 1) detect if values1 crosses from below to above values2 (crossup)
# 2) detect if values1 crosses from above to below values2 (crossdown)
from trader.lib.struct.CircularArray import CircularArray


class Crossover2(object):
    def __init__(self, window=12):
        self.window = window

        self.values1 = CircularArray(window=self.window, track_minmax=False)
        self.values2 = CircularArray(window=self.window, track_minmax=False)
        self.timestamps = CircularArray(window=self.window, track_minmax=False)
        self.age = 0
        self.last_age = 0
        self.values_under = False
        self.values_over = False
        # use for detecting the value where crossover took place
        self.values1_under_max_value = 0
        self.values1_over_min_value = 0
        self.crossup = False
        self.crossdown = False
        self.crossup_value = 0
        self.crossdown_value = 0
        self.crossup_ts = 0
        self.crossdown_ts = 0

    def update(self, value1, value2, ts=0):
        self.values1.add(float(value1))
        self.values2.add(float(value2))
        self.timestamps.add(ts)
        if self.timestamps.length() < self.window:
            return
        values2_last_value = self.values2.last_value()
        if self.values1.first_value() < values2_last_value <= self.values1.last_value():
            if self.crossup_ts and self.crossdown_ts < self.crossup_ts:
                return
            if self.values1.last_value() == values2_last_value:
                self.crossup_value = values2_last_value
                self.crossup_ts = ts
            elif ts:
                # find exact cross up point
                index_low = -1
                index_high = -1
                values = self.values1.values_ordered()
                timestamps = self.timestamps.values_ordered()
                for i in range(len(values)-1, 0, -1):
                    if values[i] >= values2_last_value: index_high = i
                    else: break
                for i in range(0, len(values)):
                    if values[i] <= values2_last_value: index_low = i
                    else: break
                index = int((index_low + index_high) / 2)
                self.crossup_value = values[index]
                self.crossup_ts = timestamps[index]
            self.crossup = True
        elif self.values1.first_value() >= values2_last_value > self.values1.last_value():
            if self.crossup_ts and self.crossdown_ts < self.crossup_ts:
                return
            if self.values1.first_value() == values2_last_value:
                self.crossdown_value = values2_last_value
                self.crossdown_ts = ts
            elif ts:
                # find exact cross down point
                index_low = -1
                index_high = -1
                values = self.values1.values_ordered()
                timestamps = self.timestamps.values_ordered()
                for i in range(len(values) - 1, 0, -1):
                    if values[i] <= values2_last_value:
                        index_low = i
                    else:
                        break
                for i in range(0, len(values)):
                    if values[i] >= values2_last_value:
                        index_high = i
                    else:
                        break
                index = int((index_low + index_high) / 2)
                self.crossdown_value = values[index]
                self.crossdown_ts = timestamps[index]
            self.crossdown = True

    # detect if value1 crosses up over value2
    def crossup_detected(self, clear=True):
        result = False
        if self.crossup:
            result = True
            if clear:
                self.crossup = False
        return result

    # detect if values1 crossed down under values2
    def crossdown_detected(self, clear=True):
        result = False
        if self.crossdown:
            result = True
            if clear:
                self.crossdown = False
        return result

    def clear(self):
        self.crossup = False
        self.crossdown = False
