from trader.lib.MovingTimeSegment.MTS import MTS

class MTS_ATR(object):
    def __init__(self, window=14, win_secs=60):
        self.window = window
        self.win_secs = win_secs
        self.last_close = 0.0
        self.trs = []
        self._tr_sum = 0
        self.age = 0
        self.atr = 0.0
        self.prior_atr = 0.0
        self.result = 0
        self.mts = MTS(seconds=self.win_secs)

    def ready(self):
        return self.mts.ready()

    def update(self, value, ts):
        self.mts.update(value, ts)

        if not self.mts.ready():
            return self.result

        high = self.mts.max()
        low = self.mts.min()
        if not len(self.trs):
            tr = high - low
        else:
            tr = max([high - low, abs(high - self.last_close), abs(low - self.last_close)])
        if len(self.trs) < self.window - 1:
            self.trs.append(tr)
            self._tr_sum += tr
            self.atr = tr
        elif self.atr == 0:
            self.trs.append(tr)
            self._tr_sum += tr
            self.atr = self._tr_sum / len(self.trs)
            self.trs[self.age] = self.atr
        else:
            self.atr = ((self.prior_atr * (self.window-1.0)) + tr) / self.window
            self.trs[self.age] = self.atr

        self.last_close = self.mts.first_value()
        self.prior_atr = self.atr
        self.age = (self.age + 1) % self.window
        self.result = self.atr
        return self.result
