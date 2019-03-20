from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.indicator.OBV import OBV


class MTSOBVSum(object):
    def __init__(self, seconds=3600):
        self.seconds = seconds
        self.mts = MovingTimeSegment(seconds=self.seconds)
        self.obv = OBV()
        self.result = 0

    def ready(self):
        return self.mts.ready()

    def update(self, close, volume, ts):
        self.obv.update(close, volume)
        self.mts.update(self.obv.result, ts)
        self.result = self.mts.get_sum()
        return self.result
