# determine if movement of MA is essentially a flat line, to filter out non-active symbols
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.indicator.EMA import EMA


class MTSFlatLine(object):
    def __init__(self, seconds=(3600*4), cutoff_percent=0.01):
        self.seconds = seconds
        self.cutoff_percent = cutoff_percent
        self.ema = EMA(200, scale=24)
        self.mts = MovingTimeSegment(seconds=self.seconds, value_smoother=self.ema, disable_fmm=True)
        self.result = 0

    def update(self, value, ts):
        self.mts.update(value, ts)

    def is_flat_line(self):
        if not self.mts.ready():
            return False

        first_value = self.mts.first_value()
        last_value = self.mts.last_value()
        if not first_value or not last_value:
            return False

        self.result = 100 * (last_value - first_value) / first_value
        if abs(self.result) <= self.cutoff_percent:
            return True

        return False
