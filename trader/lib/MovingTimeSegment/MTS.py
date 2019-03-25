# New version of MovingTimeSegment (MTS) based on MTSCircularArray class
# Given a specified time segment, only keep track of newest values no older than the set time segment
from trader.lib.MovingTimeSegment.native.MTSCircularArray import MTSCircularArray


class MTS(object):
    def __init__(self, seconds=0, minutes=0, value_smoother=None, percent_smoother=None, disable_fmm=False):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += minutes * 60
        self.seconds_ts = 1000 * self.seconds
        self.mts_array = MTSCircularArray(win_secs=self.seconds, max_win_size=self.seconds, minmax=True)
        self.full = False
        self.disable_fmm = disable_fmm
        self.value_smoother = value_smoother
        self.percent_smoother = percent_smoother

    def empty(self):
        return self.mts_array.__len__() == 0

    def ready(self):
        return self.mts_array.current_size != 0

    def update(self, value, ts):
        if self.value_smoother:
            svalue = self.value_smoother.update(value)
        else:
            svalue = value

        self.mts_array.add(svalue, ts)

    # remove all values and timestamps before argument ts
    # def remove_before_ts(self, ts):
    #     cnt = self.timestamps.index(ts)
    #
    #     if not self.disable_fmm:
    #         self.fmm.remove(cnt)
    #
    #     for i in range(0, cnt):
    #         self._sum -= self.values[i]
    #         self._sum_count -= 1
    #
    #     self.timestamps = self.timestamps[cnt:]
    #     self.values = self.values[cnt:]
    #
    #     if not self.disable_fmm:
    #         self.min_value = self.fmm.min()
    #         self.max_value = self.fmm.max()

    def get_sum(self):
        return self.mts_array.get_sum()

    def get_sum_count(self):
        return self.mts_array.get_sum_count()

    def min(self):
        if not self.ready():
            return 0
        return self.mts_array.min_value()

    def max(self):
        if not self.ready():
            return 0
        return self.mts_array.max_value()

    def get_values(self):
        return self.mts_array.values(ordered=True)

    def get_timestamps(self):
        return self.mts_array.timestamps(ordered=True)

    def value_count(self):
        return self.mts_array.length()

    def first_value(self):
        if not self.ready():
            return 0
        return self.mts_array.first_value()

    def last_value(self):
        if not self.ready():
            return 0
        return self.mts_array.last_value()

    def diff(self):
        if not self.ready():
            return 0
        return self.mts_array.last_value() - self.mts_array.first_value()

    def diff_ts(self):
        if not self.ready():
            return 0
        return self.mts_array.last_ts() - self.mts_array.first_ts()

    def percent_change(self):
        if not self.ready():
            return None
        value1 = self.mts_array.first_value()
        value2 = self.mts_array.last_value()
        if value1 == value2 or value1 == 0:
            return None

        if self.percent_smoother:
            result = self.percent_smoother.update(100.0 * (value2 - value1) / value1)
        else:
            result = 100.0 * (value2 - value1) / value1

        return result
