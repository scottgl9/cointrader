# TimeSegmentPercentChange: Track percent change of values for a given time interval
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment


class MTSPercentChange(object):
    def __init__(self, seconds=0, minutes=0, tsv=None, smoother=None, disable_fmm=True,
                 track_percent=False, tsv_percent=None):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += int(minutes) * 60
        self.seconds_ts = 1000 * self.seconds

        if tsv:
            self.tsv = tsv
        else:
            self.tsv = MovingTimeSegment(seconds, disable_fmm=disable_fmm)
        self.smoother = smoother
        self.track_percent = track_percent
        self.tsv_percent = None
        if self.track_percent:
            if tsv_percent:
                self.tsv_percent = tsv_percent
            else:
                self.tsv_percent = MovingTimeSegment(seconds, disable_fmm=disable_fmm)

    def ready(self):
        return self.tsv.ready()

    def update(self, value, ts, percent_seconds=0):
        if self.smoother:
            value = self.smoother.update(value, ts)
        self.tsv.update(value, ts)

        if self.tsv_percent:
            self.tsv_percent.update(self.get_percent_change(seconds=percent_seconds), ts)

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
        #if self.smoother:
        #    result = self.smoother.update(result)
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
