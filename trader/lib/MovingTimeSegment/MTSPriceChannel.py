from trader.indicator.EMA import EMA
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.ValueLag import ValueLag


class MTSPriceChannel(object):
    def __init__(self, seconds=0, minutes=0, lag_window=3, min_smoother=None, max_smoother=None):
        self.tsv = MovingTimeSegment(seconds, minutes)

        if min_smoother:
            self.min_smoother = min_smoother
        else:
            self.min_smoother = EMA(12, scale=24)

        if max_smoother:
            self.max_smoother = max_smoother
        else:
            self.max_smoother = EMA(12, scale=24)

        self.minimum = 0
        self.maximum = 0
        self.mid = 0
        self.result = 0
        self.last_result = 0
        self.value_lag = None
        self.lag_window = lag_window

        if self.lag_window != 0:
            self.value_lag = ValueLag(window=lag_window)

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

    def median_diff(self):
        if self.last_result == 0 or self.result == 0:
            return 0
        return self.result - self.last_result

    def median_trend_up(self):
        return self.median_diff() > 0

    def median_trend_down(self):
        return self.median_diff() < 0

    def update(self, value, ts):
        self.tsv.update(value, ts)

        if not self.tsv.ready():
            return self.result

        if self.value_lag:
            self.last_result = self.value_lag.update(self.result)
        else:
            self.last_result = self.result

        self.minimum = self.min_smoother.update(self.tsv.min())
        self.maximum = self.max_smoother.update(self.tsv.max())
        if self.minimum == 0 or self.maximum == 0:
            self.mid = 0
        else:
            self.mid = (self.minimum + self.maximum) / 2.0

        self.result = self.mid

        return self.result
