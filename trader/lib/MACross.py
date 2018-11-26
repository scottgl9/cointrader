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
        self.last_value = 0
        self.cross_ts = 0
        self.last_cross_ts = 0
        self.cross_up_ts = 0
        self.last_cross_up_ts = 0
        self.cross_down_ts = 0
        self.last_cross_down_ts = 0
        self.cross_up_value = 0
        self.last_cross_up_value = 0
        self.cross_down_value = 0
        self.last_cross_down_value = 0
        self.cross_up = False
        self.cross_down = False

        self.ma1 = self.indicator(self.ema_win1, scale=self.scale)
        self.ma2 = self.indicator(self.ema_win2, scale=self.scale)
        self.cross = Crossover2(window=10)

    # ma1 and ma2 allow to pass in an indicator from another MACross
    # that is already being updated, so that we don't have to compute
    # for example, EMA50(value) twice, instead we can re-use from another MACross instance
    def update(self, value, ts, ma1=None, ma2=None):
        if not ma1:
            self.ma1.update(value)
            ma1_result = self.ma1.result
        else:
            ma1_result = ma1.result

        if not ma2:
            self.ma2.update(value)
            ma2_result = self.ma2.result
        else:
            ma2_result = ma2.result

        if ma1_result != 0 and ma2_result != 0:
            self.cross.update(ma1_result, ma2_result)

        if self.cross.crossup_detected():
            self.cross_up = True
            self.cross_down = False
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_up_ts = self.cross_up_ts
            self.cross_up_ts = ts
            self.last_cross_up_value = self.cross_up_value
            self.cross_up_value = value
        elif self.cross.crossdown_detected():
            self.cross_up = False
            self.cross_down = True
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_down_ts = self.cross_down_ts
            self.cross_down_ts = ts
            self.last_cross_down_value = self.cross_down_value
            self.cross_down_value = value

        self.last_ts = ts
        self.last_value = value

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

    def get_ma1_diff(self):
        if self.ma1.result == 0 or self.ma1.last_result == 0:
            return 0
        return self.ma1.result - self.ma1.last_result

    def get_ma2_diff(self):
        if self.ma2.result == 0 or self.ma2.last_result == 0:
            return 0
        return self.ma2.result - self.ma2.last_result

    def ma1_trend_up(self):
        return self.get_ma1_diff() > 0

    def ma1_trend_down(self):
        return self.get_ma1_diff() < 0

    def ma2_trend_up(self):
        return self.get_ma2_diff() > 0

    def ma2_trend_down(self):
        return self.get_ma2_diff() < 0

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

    def get_crossup_below(self):
        if self.cross_up_value > self.last_value:
            return True
        return False

    def get_crossdown_above(self):
        if self.cross_down_value < self.last_value:
            return True
        return False
