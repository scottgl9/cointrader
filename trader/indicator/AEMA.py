# Auto-Scaling Exponential Moving Average (EMA) concept by Scott Glover
from .IndicatorBase import IndicatorBase
from trader.indicator.SMA import SMA
from trader.lib.ValueLag import ValueLag


class AEMA(IndicatorBase):
    def __init__(self, win=1, scale_interval_secs=60, lag_window=3):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.result = 0.0
        self.last_result = 0.0
        self.win = float(win)
        self.last_scale = 1
        self.scale = 1
        self.scale_interval_secs = scale_interval_secs
        self.sma = SMA(win)
        self.count = 0
        self.esf = 0.0
        # count number of updates in set time interval
        self.auto_last_ts = 0
        self.auto_counter = 0
        self.value_lag = None
        self.lag_window = lag_window
        self.slope = None

        if self.lag_window != 0:
            self.value_lag = ValueLag(window=lag_window)

    def ready(self):
        return self.count == self.win

    def update(self, price, ts=0):
        if not self.auto_last_ts:
            self.auto_last_ts = ts

        self.auto_counter += 1

        if (ts - self.auto_last_ts) > self.scale_interval_secs * 1000:
            self.scale = float(self.auto_counter)
            self.auto_counter = 0
            self.auto_last_ts = ts

        if self.count < self.win:
            self.result = self.sma.update(float(price))
            self.count += 1
            return self.result

        #if self.result == 0:
        #    esf = 2.0 / (self.win * self.scale)
        #    last_result = self.sma.update(float(price))
        #    self.result = float(price) * esf + last_result - 1 * (1 - esf)
        #else:
        last_result = self.result

        if self.esf == 0.0 or self.scale != self.last_scale:
            if self.win == 1:
                self.esf = 2.0 / (self.scale + 1.0)
            else:
                self.esf = 2.0 / (self.win * self.scale + 1.0)
            self.last_scale = self.scale

        if self.lag_window != 0:
            self.last_result = self.value_lag.update(self.result)
        else:
            self.last_result = self.result

        self.result = last_result + self.esf * (float(price) - last_result)

        return self.result

    def length(self):
        return self.count
