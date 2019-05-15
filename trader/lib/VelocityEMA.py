from trader.indicator.IndicatorBase import IndicatorBase
from trader.indicator.EMA import EMA
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment


class VelocityEMA(IndicatorBase):
    def __init__(self, window, scale=1, hourly_mode=False, percent=False):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.hourly_mode = hourly_mode
        self.percent = percent
        self.ema = EMA(window, scale=scale)
        self.mts = None
        self.lag = None
        self.prev_ema = 0
        self.result = 0
        if not self.hourly_mode:
            self.mts = MovingTimeSegment(seconds=3600)

    def ready(self):
        if self.hourly_mode:
            if self.prev_ema:
                return True
        else:
            if self.mts.ready():
                return True
        return False

    def update(self, close, ts):
        if self.mts:
            self.ema.update(close)
            self.mts.update(self.ema.result, ts)
            if not self.mts.ready() or not self.mts.first_value():
                return self.result
            first_value = self.mts.first_value()
            last_value = self.mts.last_value()
            if self.percent:
                self.result = 100.0 * (last_value - first_value) / first_value
            else:
                self.result = last_value - first_value
        else:
            # hourly_mode == True
            self.ema.update(close)
            if not self.prev_ema:
                self.prev_ema = self.ema.result
                return self.result
            if self.percent:
                self.result = 100.0 * (self.ema.result - self.prev_ema) / self.prev_ema
            else:
                self.result = self.ema.result - self.prev_ema
            self.prev_ema = self.ema.result

        return self.result
