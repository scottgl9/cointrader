# Average True Range (ATR)
from .IndicatorBase import IndicatorBase

class ATR(IndicatorBase):
    def __init__(self, window=14):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.result = 0.0
        self.window = window
        self.last_close = 0.0
        self.trs = []
        self._tr_sum = 0
        self.age = 0
        self.atr = 0.0
        self.prior_atr = 0.0

    def update(self, close, low=0, high=0):
        if not len(self.trs):
            tr = high - low
        else:
            tr = max([high - low, abs(high - self.last_close), abs(low - self.last_close)])
        if len(self.trs) < self.window - 1:
            self.trs.append(tr)
            self._tr_sum += tr
            self.atr = tr
        elif self.atr == 0.0:
            self.trs.append(tr)
            self._tr_sum += tr
            self.atr = self._tr_sum / self.window
            self.trs[self.age] = self.atr
        else:
            self.atr = ((self.prior_atr * (self.window-1.0)) + tr) / self.window
            self.trs[self.age] = self.atr

        self.last_close = close
        self.prior_atr = self.atr
        self.age = (self.age + 1) % self.window
        self.result = self.atr
        return self.result
