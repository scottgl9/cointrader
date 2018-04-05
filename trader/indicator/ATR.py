import numpy as np


class ATR:
    def __init__(self, window=14):
        self.result = 0.0
        self.window = window
        self.last_close = 0.0
        self.trs = []
        self.age = 0
        self.atr = 0.0
        self.prior_atr = 0.0

    def update(self, close, low, high):
        if len(self.trs) == 0.0:
            tr = high - low
        else:
            tr = max([high - low, abs(high - self.last_close), abs(low - self.last_close)])
        if len(self.trs) < self.window - 1:
            self.trs.append(tr)
            self.atr = tr
        elif self.atr == 0.0:
            self.trs.append(tr)
            self.atr = np.sum(np.array(self.trs)) / len(self.trs)
            self.trs[self.age] = self.atr
        else:
            self.atr = ((self.prior_atr * (self.window-1.0)) + tr) / self.window
            self.trs[self.age] = self.atr

        self.last_close = close
        self.prior_atr = self.atr
        self.age = (self.age + 1) % self.window
        self.result = self.atr
        return self.result
