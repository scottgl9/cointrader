from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA

class MACross(object):
    def __init__(self, ema_win1=12, ema_win2=26, scale=24, cross_timeout=0, indicator=None):
        if not indicator:
            self.indicator = EMA
        else:
            self.indicator = indicator

        self.scale = scale
        self.ema_win1 = ema_win1
        self.ema_win2 = ema_win2

        # cross_timeout is how long after a cross that we reset the cross to false (0 means no timeout)
        self.cross_timeout = cross_timeout
        self.last_ts = 0
        self.cross_ts = 0
        self.last_cross_ts = 0
        self.cross_up_ts = 0
        self.last_cross_up_ts = 0
        self.cross_down_ts = 0
        self.last_cross_down_ts = 0
        self.cross_up = False
        self.cross_down = False
        self.ma1 = self.indicator(self.ema_win1, scale=self.scale)
        self.ma2 = self.indicator(self.ema_win2, scale=self.scale)
        self.cross = Crossover2(window=10, cutoff=0.0)

    def update(self, value, ts):
        self.ma1.update(value)
        self.ma2.update(value)
        if self.ma1.result != 0 and self.ma2.result != 0:
            self.cross.update(self.ma1.result, self.ma2.result)

        if self.cross.crossup_detected():
            self.cross_up = True
            self.cross_down = False
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_up_ts = self.cross_up_ts
            self.cross_up_ts = ts
        elif self.cross.crossdown_detected():
            self.cross_up = False
            self.cross_down = True
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_down_ts = self.cross_down_ts
            self.cross_down_ts = ts

        self.last_ts = ts

        # implementation of cross timeout
        if self.cross_timeout != 0 and self.cross_ts != 0:
            if self.cross_up:
                if (self.last_ts - self.cross_up_ts) > self.cross_timeout:
                    self.cross_up = False
            elif self.cross_down:
                if (self.last_ts - self.cross_down_ts) > self.cross_timeout:
                    self.cross_down = False

    def get_ma1_result(self):
        return self.ma1.result

    def get_ma2_result(self):
        return self.ma2.result

    # get time difference between most recent cross up and previous cross up
    def get_crossup_ts_delta(self):
        if self.last_cross_up_ts ==0 or self.cross_up_ts == 0:
            return 0
        return (self.cross_up_ts - self.last_cross_up_ts)

    # get time difference between most recent cross down and previous cross down
    def get_crossdown_ts_delta(self):
        if self.last_cross_down_ts == 0 or self.cross_down_ts == 0:
            return 0
        return (self.cross_down_ts - self.last_cross_down_ts)

    # get time difference between most recent cross down, and most recent cross up
    # return value will depend on if the cross up was more recent, or if the cross down more recent
    def get_cross_ts_delta(self):
        if self.cross_down_ts == 0 or self.cross_up_ts == 0:
            return 0
        return abs(self.cross_up_ts - self.cross_down_ts)

    # get time difference between the previous cross down, and previous cross up
    # return value will depend on if the cross up was more recent, or if the cross down more recent
    def get_prev_cross_ts_delta(self):
        if self.last_cross_down_ts == 0 or self.last_cross_up_ts == 0:
            return 0
        return abs(self.last_cross_up_ts - self.last_cross_down_ts)
