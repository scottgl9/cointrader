# crossover detection
# 1) detect if values1 crosses from below to above values2 (crossup)
# 2) detect if values1 crosses from above to below values2 (crossdown)

# pre_window allows an additional window to check before or after crossover
# in addition to window, to verify all values in pre_window were under/over crosspoint
# before crossup/crossdown occurred
#try:
#    from trader.lib.MovingTimeSegment.native.MTSCircularArray import MTSCircularArray
#except ImportError:
from trader.lib.MovingTimeSegment.MTSCircularArray import MTSCircularArray


class MTSCrossover(object):
    def __init__(self, pre_win_secs=0, win_secs=60, check_expand=False, result_secs=0):
        self.pre_win_secs = pre_win_secs
        self.win_secs = win_secs
        self.result_secs = result_secs
        self.check_expand = check_expand

        self.diff = None
        if self.check_expand:
            self.diff = MTSCircularArray(win_secs=win_secs, max_win_size=win_secs+1, minmax=True)
        self.mtsca1 = MTSCircularArray(win_secs=win_secs, max_win_size=win_secs+1, minmax=True)
        self.mtsca2 = MTSCircularArray(win_secs=win_secs, max_win_size=win_secs+1, minmax=True)
        self.pre_mtsca1 = MTSCircularArray(win_secs=pre_win_secs, max_win_size=pre_win_secs+1, minmax=True)
        self.pre_mtsca2 = MTSCircularArray(win_secs=pre_win_secs, max_win_size=pre_win_secs+1, minmax=True)

        self.values_under = False
        self.values_over = False
        self.crossup = False
        self.crossdown = False
        self._no_cross = True
        self.last_cross_ts = 0
        self.result_start_ts = 0
        self.ts = 0

    def update(self, value1, value2, ts):
        if not self.ts:
            self.ts = ts

        self.mtsca1.add(value1, ts)
        self.mtsca2.add(value2, ts)
        if self.check_expand:
            self.diff.add(abs(value1 - value2), ts)

        if not self.mtsca1.ready():
            return

        if self.pre_win_secs:
            self.pre_mtsca1.add(self.mtsca1.first_value(), ts)
            self.pre_mtsca2.add(self.mtsca2.first_value(), ts)

            if not self.pre_mtsca1.ready():
                return

        # put a maximum time on how long crossup / crossdown stays true
        if self.result_secs and self.result_start_ts:
            if (ts - self.result_start_ts) > self.result_secs * 1000:
                self.crossup = False
                self.crossdown = False
                self.result_start_ts = 0

        if self.values_under and self.mtsca1.min_value() > self.mtsca2.max_value():
            if not self.last_cross_ts or (ts - self.last_cross_ts) > (self.pre_win_secs + self.win_secs) * 1000:
                # values1 in window were under values2, now all values1 over values2
                if not self.check_expand or self.diff.values_increasing():
                    self.values_under = False
                    self.values_over = False
                    self.crossup = True
                    self.crossdown = False
                    self._no_cross = False
                    if self.result_secs:
                        self.result_start_ts = ts
                    self.last_cross_ts = ts
        elif self.values_over and self.mtsca1.max_value() < self.mtsca2.min_value():
            if not self.last_cross_ts or (ts - self.last_cross_ts) > (self.pre_win_secs + self.win_secs) * 1000:
                # values1 in window were over values2, now all values1 under values2
                if not self.check_expand or self.diff.values_increasing():
                    self.values_over = False
                    self.values_under = False
                    self.crossdown = True
                    self.crossup = False
                    self._no_cross = False
                    if self.result_secs:
                        self.result_start_ts = ts
                    self.last_cross_ts = ts
        elif not self.values_under and not self.values_over:
            if self.mtsca1.max_value() < self.mtsca2.min_value():
                if self.pre_win_secs:
                    # make sure values1 in pre_window were also under values2
                    if self.pre_mtsca1.max_value() < self.pre_mtsca2.min_value():
                        self.values_under = True
                else:
                    # all of values1 under values2
                    self.values_under = True
                    self.values_over = False
            elif self.mtsca1.min_value() > self.mtsca2.max_value():
                if self.pre_win_secs:
                    # make sure values1 in pre_window were also over values2
                    if self.pre_mtsca1.min_value() > self.pre_mtsca2.max_value():
                        self.values_over = True
                else:
                    # all of values1 over values2
                    self.values_over = True
                    self.values_under = False

    def no_cross_detected(self):
        return self._no_cross

    # detect if value1 crosses up over value2
    def crossup_detected(self, clear=True):
        result = False
        if self.crossup:
            result = True
            if clear and not self.result_secs:
                self.crossup = False
        return result

    # detect if values1 crossed down under values2
    def crossdown_detected(self, clear=True):
        result = False
        if self.crossdown:
            result = True
            if clear and not self.result_secs:
                self.crossdown = False
        return result

    def clear(self):
        self.crossup = False
        self.crossdown = False
