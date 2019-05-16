from trader.indicator.EMA import EMA
from .Velocity import Velocity


class VelocityEMADiff(object):
    def __init__(self, win1=26, win2=200, scale=1, hourly_mode=False, percent=False):
        self.win1 = win1
        self.win2 = win2
        self.scale = scale
        self.hourly_mode = hourly_mode
        self.percent = percent
        self.v1 = Velocity(hourly_mode=self.hourly_mode, percent=self.percent)
        self.v2 = Velocity(hourly_mode=self.hourly_mode, percent=self.percent)
        self.ema1 = EMA(self.win1, scale=self.scale)
        self.ema2 = EMA(self.win2, scale=self.scale)
        self.result = 0

    def update(self, close, ts):
        self.ema1.update(close)
        self.ema2.update(close)
        self.v1.update(self.ema1.result, ts)
        self.v2.update(self.ema2.result, ts)
        if not self.v2.result:
            return self.result

        self.result = abs(self.v1.result) - abs(self.v2.result)
        return self.result
