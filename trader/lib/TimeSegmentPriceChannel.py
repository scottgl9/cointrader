from trader.indicator.EMA import EMA
from trader.lib.TimeSegmentValues import TimeSegmentValues


class TimeSegmentPriceChannel(object):
    def __init__(self, seconds=0, minutes=0, value_smoother=None, percent_smoother=None):
        self.tsv = TimeSegmentValues(seconds, minutes)
        self.min_smoother = EMA(12, scale=24)
        self.max_smoother = EMA(12, scale=24)
        self.minimum = 0
        self.maximum = 0
        self.mid = 0
        self.result = 0

    def ready(self):
        return self.tsv.ready()

    def min(self):
        return self.minimum

    def max(self):
        return self.maximum

    def median(self):
        if self.minimum == 0 or self.maximum == 0:
            return 0
        return self.mid

    def update(self, value, ts):
        self.tsv.update(value, ts)

        if not self.tsv.ready():
            return

        self.minimum = self.min_smoother.update(self.tsv.min())
        self.maximum = self.max_smoother.update(self.tsv.max())
        self.mid = (self.minimum + self.maximum) / 2.0
        self.result = self.mid

        return self.result
