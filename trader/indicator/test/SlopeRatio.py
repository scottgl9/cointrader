from trader.lib.CircularArray import CircularArray
from trader.indicator.EMA import EMA

class SlopeRatio(object):
    def __init__(self, window=50, smoother1=None, smoother2=None):
        self.window = window
        if not smoother1:
            self.smoother1 = EMA(12, scale=24)
        else:
            self.smoother1 = smoother1
        if not smoother2:
            self.smoother2 = EMA(50, scale=24)
        else:
            self.smoother2 = smoother2

        self.smoother1_values = CircularArray(window=self.window)
        self.smoother2_values = CircularArray(window=self.window)
        self.smooth_ratio = EMA(9)
        self.result = 0

    def update(self, value):
        self.smoother1.update(value)
        self.smoother2.update(value)

        self.smoother1_values.add(self.smoother1.result)
        self.smoother2_values.add(self.smoother2.result)

        if not self.smoother1_values.full() and not self.smoother1_values.full():
            return self.result

        delta1 = (self.smoother1_values.last() - self.smoother1_values.first())
        delta2 = (self.smoother2_values.last() - self.smoother2_values.first())

        if delta2 == 0:
            return self.result

        #if (delta1 < 0 and delta2) > 0 or (delta1 > 0 and delta2 < 0):
        #    return self.result

        if delta2 < 0:
            self.result = -(abs(delta1) / abs(delta2)) #self.smooth_ratio.update(delta1 / delta2)
        else:
            self.result = abs(delta1) / abs(delta2)

        return self.result
