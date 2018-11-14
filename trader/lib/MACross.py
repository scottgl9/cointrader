from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA

class MACross(object):
    def __init__(self, ema_win1, ema_win2, scale=1, indicator=None):
        if not indicator:
            self.indicator = EMA
        else:
            self.indicator = indicator

            self.last_ts = 0
            self.cross_ts = 0
            self.last_cross_ts = 0
            self.cross_up = False
            self.cross_down = False
            self.ma1 = self.indicator(ema_win1, scale=scale)
            self.ma2 = self.indicator(ema_win2, scale=scale)
            self.cross = Crossover2(window=10, cutoff=0.0)

    def update(self, value, ts):
        self.ma1.update(value)
        self.ma2.update(value)
        self.cross.update(self.ma1.result, self.ma2.result)

        if self.cross.crossup_detected():
            self.cross_up = True
            self.cross_down = False
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
        elif self.cross.crossdown_detected():
            self.cross_up = False
            self.cross_down = True
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts

        self.last_ts = ts
