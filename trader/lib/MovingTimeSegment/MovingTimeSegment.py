# Given a specified time segment, only keep track of newest values no older than the set time segment
from trader.lib.FastMinMax import FastMinMax


class MovingTimeSegment(object):
    def __init__(self, seconds=0, minutes=0, value_smoother=None, percent_smoother=None,
                 disable_fmm=False, enable_volume=False, track_ts=False):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += minutes * 60
        self.seconds_ts = 1000 * self.seconds
        self.values = []
        self.volumes = None
        self.timestamps = []
        self.track_ts = track_ts
        self.fmm = FastMinMax(track_ts=self.track_ts)
        self.full = False
        self.enable_volume = enable_volume
        if self.enable_volume:
            self.volumes = []
        self.disable_fmm = disable_fmm
        self.value_smoother = value_smoother
        self.percent_smoother = percent_smoother
        self.min_value = 0
        self.min_value_index = -1
        self.min_value_ts = 0
        self.max_value = 0
        self.max_value_index = -1
        self.max_value_ts = 0
        # track moving sum of time segment values
        self._sum = 0
        self._sum_count = 0

    def empty(self):
        if len(self.values) == 0:
            return True
        return False

    def ready(self):
        return self.full

    def update(self, value, ts, volume=0):
        if self.value_smoother:
            svalue = self.value_smoother.update(value)
        else:
            svalue = value

        if self.enable_volume:
            self.volumes.append(volume)
        self.values.append(svalue)
        self.timestamps.append(ts)

        self._sum += svalue
        self._sum_count += 1

        cnt = 0
        while (ts - self.timestamps[cnt]) > self.seconds_ts:
            cnt += 1

        if not self.disable_fmm:
            self.fmm.append(svalue)

        if cnt != 0:
            if not self.disable_fmm:
                self.fmm.remove(cnt)

            for i in range(0, cnt):
                self._sum -= self.values[i]
                self._sum_count -= 1

            self.timestamps = self.timestamps[cnt:]
            self.values = self.values[cnt:]
            if self.enable_volume:
                self.volumes = self.volumes[cnt:]
            if not self.full:
                self.full = True

        if not self.disable_fmm:
            self.min_value = self.fmm.min()
            self.max_value = self.fmm.max()
            if self.track_ts:
                self.min_value_ts = self.fmm.min_ts()
                self.max_value_ts = self.fmm.max_ts()

    # remove all values and timestamps before argument ts
    def remove_before_ts(self, ts):
        cnt = self.timestamps.index(ts)

        if not self.disable_fmm:
            self.fmm.remove(cnt)

        for i in range(0, cnt):
            self._sum -= self.values[i]
            self._sum_count -= 1

        self.timestamps = self.timestamps[cnt:]
        self.values = self.values[cnt:]
        if self.enable_volume:
            self.volumes = self.volumes[cnt:]

        if not self.disable_fmm:
            self.min_value = self.fmm.min()
            self.max_value = self.fmm.max()
            if self.track_ts:
                self.min_value_ts = self.fmm.min_ts()
                self.max_value_ts = self.fmm.max_ts()

    def get_sum(self):
        return float(self._sum)

    def get_sum_count(self):
        return self._sum_count

    def min(self):
        if not self.ready():
            return 0
        return self.min_value

    def max(self):
        if not self.ready():
            return 0
        return self.max_value

    def min_ts(self):
        return self.min_value_ts

    def max_ts(self):
        return self.max_value_ts

    def get_values(self):
        return self.values

    def get_volumes(self):
        return self.volumes

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
