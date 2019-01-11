# TimeSegmentPercentChange: Track percent change of values for a given time interval
from trader.lib.TimeSegmentValues import TimeSegmentValues


class TimeSegmentPercentChange(object):
    def __init__(self, seconds=0, minutes=0, tsv=None, smoother=None, disable_fmm=True):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += int(minutes) * 60
        self.seconds_ts = 1000 * self.seconds

        if tsv:
            self.tsv = tsv
        else:
            self.tsv = TimeSegmentValues(seconds, disable_fmm=disable_fmm)
        self.smoother = smoother

    def ready(self):
        return self.tsv.ready()

    def update(self, value, ts):
        self.tsv.update(value, ts)

    def get_values_seconds(self, seconds):
        if not self.ready() or seconds > self.seconds:
            return None

        seconds_ts = 1000.0 * seconds
        values = self.tsv.get_values()
        timestamps = self.tsv.get_timestamps()
        count = 0
        start_ts = timestamps[-1]
        for i in range(len(timestamps) - 1, 0, -1):
            if (start_ts - timestamps[i]) > seconds_ts:
                break
            count += 1

        values = values[:-count]
        if len(values) < 2:
            return None
        return values

    def get_percent_change(self, values=None, seconds=0):
        if not values:
            if seconds == 0:
                values = self.tsv.get_values()
            else:
                values = self.get_values_seconds(seconds)
        if not values:
            return 0
        result = 100.0 * (values[-1] - values[0]) / values[0]
        if self.smoother:
            result = self.smoother.update(result)
        return result

    def greater_than_percent_time_up(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if pchange >= percent:
            return True
        return False

    def less_than_percent_time_up(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if 0 <= pchange < percent:
            return True
        return False

    def greater_than_percent_time_down(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if pchange <= -percent:
            return True
        return False

    def less_than_percent_time_down(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if 0 >= pchange > -percent:
            return True
        return False

    def greater_than_percent_time(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if abs(pchange) >= percent:
            return True
        return False

    def less_than_percent_time(self, percent, seconds):
        pchange = self.get_percent_change(seconds)
        if 0 <= abs(pchange) < percent:
            return True
        return False
