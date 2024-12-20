# Exponential Moving Average (EMA)
# NOTE: The Exponentially weighted Moving Average (EWMA) is the same as the EMA

from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.SLOPE import SLOPE
from trader.indicator.SMA import SMA
from trader.lib.ValueLag import ValueLag


class EMA(IndicatorBase):
    def __init__(self, weight=26, scale=1.0, lag_window=3, slope_window=0, custom=False):
        self.result_count = 1
        #super(EMA, self).__init__(use_close=True)
        IndicatorBase.__init__(self, use_close=True)
        self.result = 0.0
        self.last_result = 0.0
        self.weight = float(weight)
        self.scale = scale
        self.sma = SMA(weight)
        self.count = 0
        self.esf = 0.0
        self.value_lag = None
        self.lag_window = lag_window
        self.slope_window = slope_window
        self.slope = None
        self.custom = custom

        if self.lag_window != 0:
            self.value_lag = ValueLag(window=lag_window)

        if self.slope_window != 0:
            self.slope = SLOPE(window=self.slope_window)

    def ready(self):
        return self.count == self.weight

    def update(self, price, ts=0):
        if self.count < self.weight:
            self.result = self.sma.update(float(price))
            self.count += 1
            return self.result

        if self.result == 0:
            esf = 2.0 / (self.weight * self.scale)
            last_result = self.sma.update(float(price))
            self.result = float(price) * esf + last_result - 1 * (1 - esf)
        else:
            last_result = self.result

            if self.esf == 0.0:
                if self.custom:
                    # this is just so we can use EMA with PMO
                    self.esf = 2.0 / (self.weight * self.scale)
                else:
                    self.esf = 2.0 / (self.weight * self.scale + 1.0)

            if self.lag_window != 0:
                self.last_result = self.value_lag.update(self.result)
            else:
                self.last_result = self.result

            self.result = last_result + self.esf * (float(price) - last_result)

        if self.slope:
            self.slope.update(self.result)

        return self.result

    def length(self):
        return self.count
