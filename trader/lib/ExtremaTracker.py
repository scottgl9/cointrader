# Track local extrema (local minimums and maximums) of price data / moving average
from trader.lib.TimeSegmentValues import TimeSegmentValues

class ExtremaTracker(object):
    def __init__(self):
        self.tsv = TimeSegmentValues(seconds=3600)

    def ready(self):
        return self.tsv.ready()

    def update(self, value, ts):
        self.tsv.update(value, ts)

        if not self.ready():
            return

