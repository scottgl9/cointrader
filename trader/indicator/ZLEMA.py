from trader.indicator.EMA import EMA
from trader.lib.ValueLag import ValueLag

class ZLEMA(object):
    def __init__(self, window=12, scale=1.0):
        self.window = window
        self.ema = EMA(weight=window, scale=scale)
        self.values = []
        self.age = 0
        self.result = 0

    def update(self, value):
        if len(self.values) < self.window:
            result = self.ema.update(float(value))
            self.values.append(result)
            self.result = result
        else:
            self.values[int(self.age)] = float(value)

            lag = ((self.age - 1) / 2) % self.window
            self.result = self.ema.update(2.0 * self.values[int(self.age)] - self.values[lag])

        self.age = (self.age + 1) % self.window

        return self.result

class DZLEMA(object):
    def __init__(self, window=12, scale=1.0, lagging=False, lag_window=3):
        self.zlema1 = ZLEMA(window=window, scale=scale)
        self.zlema2 = ZLEMA(window=window, scale=scale)
        self.result = 0
        self.last_result = 0
        self.lagging = lagging
        self.value_lag = None
        if self.lagging:
            self.value_lag = ValueLag(window=lag_window)

    def update(self, value):
        self.result = self.zlema2.update(self.zlema1.update(value))

        if self.lagging:
            self.last_result = self.value_lag.update(self.result)
        else:
            self.last_result = self.result

        return self.result
