# moving estimate of window size based on specified time interval, and updated with timestamps
from trader.lib.CircularArray import CircularArray

class TimeWindow(object):
    def __init__(self, seconds, max_win_count=5000):
        # desired window size in seconds
        self.seconds = seconds
        self.max_win_count = max_win_count
        self.timestamps = CircularArray(window=self.max_win_count)
        self.result = 0

    def update(self, ts):
        if self.timestamps.empty():
            self.timestamps.add(ts)
            return self.result

        if (ts - self.timestamps.first()) > 1000 * self.seconds:
            self.result = len(self.timestamps)
            self.timestamps.reset()
            self.timestamps.add(ts)
            return self.result

        self.timestamps.add(ts)
        return self.result
