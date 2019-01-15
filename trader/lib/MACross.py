from trader.lib.Crossover2 import Crossover2
from trader.indicator.EMA import EMA
from trader.lib.ValueLag import ValueLag

class MACross(object):
    def __init__(self, ema_win1=0, ema_win2=0, scale=0, cross_window=10, cross_timeout=0,
                 lag_window=3, indicator=None):
        #if not indicator:
        #    self.indicator = EMA
        #else:
        self.indicator = indicator

        self.scale = scale
        self.ema_win1 = ema_win1
        self.ema_win2 = ema_win2
        self.lag_window = lag_window

        # cross_timeout is how long after a cross that we reset the cross to false (0 means no timeout)
        self.cross_timeout = cross_timeout
        self.cross_window = cross_window
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

        self.pre_cross_up_min_value = 0
        self.pre_cross_up_max_value = 0
        self.post_cross_up_min_value = 0
        self.post_cross_up_max_value = 0

        self.pre_cross_down_min_value = 0
        self.pre_cross_down_max_value = 0
        self.post_cross_down_min_value = 0
        self.post_cross_down_max_value = 0

        self.cross_up = False
        self.cross_down = False

        self.ma1 = None
        self.ma2 = None
        self.ma1_result = 0
        self.ma2_result = 0
        self.ma1_last_result = 0
        self.ma2_last_result = 0

        if not self.indicator and self.lag_window != 0:
            self.ma1_lag = ValueLag(lag_window)
            self.ma2_lag = ValueLag(lag_window)
        else:
            self.ma1_lag = None
            self.ma2_lag = None

        if self.indicator and self.ema_win1:
            self.ma1 = self.indicator(self.ema_win1, scale=self.scale, lag_window=self.lag_window)
        if self.indicator and self.ema_win2:
            self.ma2 = self.indicator(self.ema_win2, scale=self.scale, lag_window=self.lag_window)

        self.cross = Crossover2(window=self.cross_window)

    def update_min_max_values(self, value, ts):
        if self.cross_up:
            if value > self.post_cross_up_max_value:
                self.post_cross_up_max_value = value
            if self.post_cross_up_min_value == 0 or value < self.post_cross_up_min_value:
                self.post_cross_up_min_value = value
        elif self.cross_down:
            if value > self.post_cross_down_max_value:
                self.post_cross_down_max_value = value
            if self.post_cross_down_min_value == 0 or value < self.post_cross_down_min_value:
                self.post_cross_down_min_value = value

    # ma1 and ma2 allow to pass in an indicator from another MACross
    # that is already being updated, so that we don't have to compute
    # for example, EMA50(value) twice, instead we can re-use from another MACross instance
    def update(self, value, ts, ma1=None, ma2=None, ma1_result=0, ma2_result=0):
        if self.ma1 and not ma1 and ma1_result == 0:
            self.ma1.update(value)
            self.ma1_result = self.ma1.result
            self.ma1_last_result = self.ma1.last_result
            ma1_result = self.ma1.result
            ma1_ready = self.ma1.ready()
        elif ma1_result == 0 and ma1:
            ma1_result = ma1.result
            self.ma1.result = ma1.result
            ma1_ready = ma1.ready()
        else:
            self.ma1_result = ma1_result
            if ma1_result != 0:
                ma1_ready = True
            else:
                ma1_ready = False

        if self.ma1 and not ma2 and ma2_result == 0:
            self.ma2.update(value)
            self.ma2_result = self.ma2.result
            self.ma2_last_result = self.ma2.last_result
            ma2_result = self.ma2.result
            ma2_ready = self.ma2.ready()
        elif ma2_result == 0 and ma2:
            ma2_result = ma2.result
            self.ma2.result = ma2.result
            ma2_ready = ma2.ready()
        else:
            self.ma2_result = ma2_result
            if ma2_result != 0:
                ma2_ready = True
            else:
                ma2_ready = False

        if not self.indicator and self.ma1_lag:
            self.ma1_last_result = self.ma1_lag.update(self.ma1_result)
        if not self.indicator and self.ma2_lag:
            self.ma2_last_result = self.ma2_lag.update(self.ma2_result)

        if not ma1_ready or not ma2_ready:
            return

        if ma1_result != 0 and ma2_result != 0:
            self.cross.update(ma1_result, ma2_result)

        self.update_min_max_values(value, ts)

        if self.cross.crossup_detected():
            self.cross_up = True
            self.cross_down = False
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_up_ts = self.cross_up_ts
            self.cross_up_ts = ts
            self.last_cross_up_value = self.cross_up_value
            self.cross_up_value = value
            self.pre_cross_up_min_value = self.post_cross_up_min_value
            self.pre_cross_up_max_value = self.post_cross_up_max_value
            self.post_cross_up_min_value = 0
            self.post_cross_up_max_value = 0
        elif self.cross.crossdown_detected():
            self.cross_up = False
            self.cross_down = True
            self.last_cross_ts = self.cross_ts
            self.cross_ts = ts
            self.last_cross_down_ts = self.cross_down_ts
            self.cross_down_ts = ts
            self.last_cross_down_value = self.cross_down_value
            self.cross_down_value = value
            self.pre_cross_down_min_value = self.post_cross_down_min_value
            self.pre_cross_down_max_value = self.post_cross_down_max_value
            self.post_cross_down_min_value = 0
            self.post_cross_down_max_value = 0

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
        if self.ma1:
            return self.ma1.result
        return self.ma1_result

    def get_ma2_result(self):
        if self.ma2:
            return self.ma2.result
        return self.ma2_result

    def get_ma1_diff(self):
        if self.ma1_result == 0 or self.ma1_last_result == 0:
            return 0
        return self.ma1_result - self.ma1_last_result

    def get_ma2_diff(self):
        if self.ma2_result == 0 or self.ma2_last_result == 0:
            return 0
        return self.ma2_result - self.ma2_last_result

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

    def get_pre_crossup_low(self):
        return self.pre_cross_up_min_value

    def get_pre_crossup_high(self):
        return self.pre_cross_up_max_value

    def get_pre_crossdown_low(self):
        return self.pre_cross_down_min_value

    def get_pre_crossdown_high(self):
        return self.pre_cross_down_max_value

    def get_pre_crossup_low_percent(self):
        if self.pre_cross_up_min_value == 0:
            return 0
        return 100.0 * (self.cross_up_value - self.pre_cross_up_min_value) / self.pre_cross_up_min_value

    def get_pre_crossdown_high_percent(self):
        if self.pre_cross_down_max_value == 0:
            return 0
        return 100.0 * (self.pre_cross_down_max_value - self.cross_down_value) / self.pre_cross_down_max_value

    def is_near_post_crossup_max(self, value=0, cutoff=0.01, percent=0.5):
        if self.post_cross_up_max_value == 0 or self.cross_up_value == 0:
            return False

        if self.cross_up_ts == 0 or self.cross_down_ts > self.cross_up_ts:
            return False

        if value == 0:
            value = self.last_value

        if abs((self.cross_up_value - self.post_cross_up_max_value) / self.cross_up_value) < cutoff:
            return False

        if abs(100.0 * (value - self.post_cross_up_max_value) / self.post_cross_up_max_value) <= percent:
            return True
        return False
