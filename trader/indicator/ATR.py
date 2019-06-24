# Average True Range (ATR)
from .IndicatorBase import IndicatorBase

class ATR(IndicatorBase):
    def __init__(self, window=14):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.result = 0.0
        self.window = window
        self.last_close = 0.0
        self._tr_sum = 0
        self.count = 0
        self.atr = 0
        self.prior_atr = 0

    def update(self, close, low, high):
        if not self.count:
            tr = high - low
        else:
            tr = max([high - low, abs(high - self.last_close), abs(low - self.last_close)])
        if self.count < self.window - 1:
            self._tr_sum += tr
            self.count += 1
        elif not self.atr:
            self._tr_sum += tr
            self.atr = self._tr_sum / self.window
            self.count += 1
        else:
            self.prior_atr = self.atr
            self.atr = ((self.prior_atr * float(self.window - 1)) + tr) / self.window

        self.last_close = close
        self.result = self.atr
        return self.result
