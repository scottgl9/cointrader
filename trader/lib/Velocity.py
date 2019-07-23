# Hourly velocity
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment

class Velocity(IndicatorBase):
    def __init__(self, hourly_mode=False, percent=False):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.hourly_mode = hourly_mode
        self.percent = percent
        self.mts = None
        self.lag = None
        self.prev_value = 0
        self.result = 0
        if not self.hourly_mode:
            self.mts = MovingTimeSegment(seconds=3600)

    def ready(self):
        if self.hourly_mode:
            if self.prev_value:
                return True
        else:
            if self.mts.ready():
                return True
        return False

    def update(self, value, ts):
        if self.mts:
            self.mts.update(value, ts)
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
            if not self.prev_value:
                self.prev_value = value
                return self.result
            if self.percent:
                self.result = 100.0 * (value - self.prev_value) / self.prev_value
            else:
                self.result = value - self.prev_value
            self.prev_value = value

        return self.result
