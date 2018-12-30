from trader.lib.TimeSegmentValues import TimeSegmentValues


class TimeSegmentPercentChange(object):
    def __init__(self, seconds, minutes, tsv=None):
        self.seconds = seconds
        if minutes != 0:
            self.seconds += minutes * 60
        self.seconds_ts = 1000 * self.seconds

        if tsv:
            self.tsv = tsv
        else:
            self.tsv = TimeSegmentValues(seconds)

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

    def greater_than_percent_time_up(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if pchange >= percent:
            return True
        return False

    def less_than_percent_time_up(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if 0 <= pchange < percent:
            return True
        return False

    def greater_than_percent_time_down(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if pchange <= -percent:
            return True
        return False

    def less_than_percent_time_down(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if 0 >= pchange > -percent:
            return True
        return False

    def greater_than_percent_time(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if abs(pchange) >= percent:
            return True
        return False

    def less_than_percent_time(self, percent, seconds):
        values = self.get_values_seconds(seconds)
        if not values:
            return False
        pchange = 100.0 * (values[-1] - values[0]) / values[0]
        if 0 <= abs(pchange) < percent:
            return True
        return False
