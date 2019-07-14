from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment


class MTS_SMA(object):
    def __init__(self, seconds=60):
        self.seconds = seconds
        self.mts = MovingTimeSegment(seconds=self.seconds, disable_fmm=False)
        self.result = 0

    def ready(self):
        return self.mts.ready()

    def update(self, value, ts):
        self.mts.update(value, ts)
        if not self.mts.ready():
            return False

        count = self.mts.get_sum_count()
        if not count:
            return self.result

        self.result = self.mts.get_sum() / count
        return self.result

    def first_value(self):
        return self.mts.first_value()

    def last_value(self):
        return self.mts.last_value()

    def diff(self):
        return self.mts.last_value() - self.mts.first_value()

    def min(self):
        return self.mts.min()

    def max(self):
        return self.mts.max()

    def avg(self):
        return self.result
