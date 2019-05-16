# Acceleration
from trader.indicator.IndicatorBase import IndicatorBase
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.Velocity import Velocity


class Acceleration(IndicatorBase):
    def __init__(self, hourly_mode=False, percent=False):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.hourly_mode = hourly_mode
        self.percent = percent
        self.velocity = Velocity(hourly_mode, percent)
        self.mts = None
        self.lag = None
        if not self.hourly_mode:
            self.mts = MovingTimeSegment(seconds=3600)
        self.prev_velocity = 0
        self.result = 0

    def ready(self):
        if self.mts:
            return self.mts.ready()
        elif self.prev_velocity:
            return True
        return False

    def update(self, close, ts):
        if self.mts:
            self.velocity.update(close, ts)
            if not self.velocity.ready():
                return self.result
            self.mts.update(self.velocity.result, ts)
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
            self.velocity.update(close, ts)
            if not self.prev_velocity:
                self.prev_velocity = self.velocity.result
                return self.result
            if self.percent:
                self.result = 100.0 * (self.velocity.result - self.prev_velocity) / self.prev_velocity
            else:
                self.result = self.velocity.result - self.prev_velocity
            self.prev_velocity = self.velocity.result

        return self.result
