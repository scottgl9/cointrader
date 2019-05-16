# Acceleration of EMA
from trader.indicator.IndicatorBase import IndicatorBase
from trader.indicator.EMA import EMA
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.VelocityEMA import VelocityEMA


class AccelEMA(IndicatorBase):
    def __init__(self, window, scale=1, hourly_mode=False, percent=False):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.hourly_mode = hourly_mode
        self.percent = percent
        self.velocity_ema = VelocityEMA(window, scale, hourly_mode, percent)
        self.mts = None
        self.lag = None
        if not self.hourly_mode:
            self.mts = MovingTimeSegment(seconds=3600)
        self.prev_velocity = 0
        self.result = 0

    def update(self, close, ts):
        if self.mts:
            self.velocity_ema.update(close, ts)
            if not self.velocity_ema.ready():
                return self.result
            self.mts.update(self.velocity_ema.result, ts)
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
            self.velocity_ema.update(close, ts)
            if not self.prev_velocity:
                self.prev_velocity = self.velocity_ema.result
                return self.result
            if self.percent:
                self.result = 100.0 * (self.velocity_ema.result - self.prev_velocity) / self.prev_velocity
            else:
                self.result = self.velocity_ema.result - self.prev_velocity
            self.prev_velocity = self.velocity_ema.result

        return self.result
