# MTSCrossover with 3 lines
from .MTSCrossover2 import MTSCrossover2


class MTSCrossover3(object):
    def __init__(self, win_secs=60):
        self.win_secs = win_secs
        self.cross12 = MTSCrossover2(win_secs=self.win_secs)
        self.cross23 = MTSCrossover2(win_secs=self.win_secs)
        self.cross13 = MTSCrossover2(win_secs=self.win_secs)
        self.cross12_up = False
        self.last_cross12_up_value = 0
        self.cross12_up_value = 0
        self.cross12_up_ts = 0
        self.cross12_down = False
        self.last_cross12_down_value = 0
        self.cross12_down_value = 0
        self.cross12_down_ts = 0
        self.cross23_up = False
        self.cross23_up_value = 0
        self.cross23_up_ts = 0
        self.cross23_down = False
        self.cross23_down_value = 0
        self.cross23_down_ts = 0
        self.cross13_up = False
        self.last_cross13_up_value = 0
        self.cross13_up_value = 0
        self.cross13_up_ts = 0
        self.cross13_down = False
        self.last_cross13_down_value = 0
        self.cross13_down_value = 0
        self.cross13_down_ts = 0
        self.crossup = False
        self.crossdown = False

    def update(self, value1, value2, value3, ts):
        self.cross12.update(value1, value2, ts)
        if self.cross12.crossup_detected():
            self.cross12_up = True
            self.last_cross12_up_value = self.cross12_up_value
            self.cross12_up_value = self.cross12.crossup_value
            self.cross12_up_ts = self.cross12.crossup_ts
        elif self.cross12.crossdown_detected():
            self.cross12_down = True
            self.last_cross12_down_value = self.cross12_down_value
            self.cross12_down_value = self.cross12.crossdown_value
            self.cross12_down_ts = self.cross12.crossdown_ts
        self.cross23.update(value2, value3, ts)
        if self.cross23.crossup_detected():
            self.cross23_up = True
            self.cross23_up_value = self.cross23.crossup_value
            self.cross23_up_ts = self.cross23.crossup_ts
        elif self.cross23.crossdown_detected():
            self.cross23_down = True
            self.cross23_down_value = self.cross23.crossdown_value
            self.cross23_down_ts = self.cross23.crossdown_ts
        self.cross13.update(value1, value3, ts)
        if self.cross13.crossup_detected():
            self.cross13_up = True
            self.last_cross13_up_value = self.cross13_up_value
            self.cross13_up_value = self.cross13.crossup_value
            self.cross13_up_ts = self.cross13.crossup_ts
        elif self.cross13.crossdown_detected():
            self.cross13_down = True
            self.last_cross13_down_value = self.cross13_down_value
            self.cross13_down_value = self.cross13.crossdown_value
            self.cross13_down_ts = self.cross13.crossdown_ts

    # determine if values1 crossed up over both values3 and values2
    def crossup_detected(self):
        if not self.cross12_up_ts or not self.cross13_up_ts or not self.cross23_up_ts:
            return False
        if self.cross12_down_ts > self.cross12_up_ts or self.cross13_down_ts > self.cross13_up_ts or self.cross23_down_ts > self.cross23_up_ts:
            return False
        if self.cross13_up_ts <= self.cross23_up_ts and not self.crossup:
            self.crossdown = False
            self.crossup = True
            return True
        return False

    # determine if values1 cross down over both values2 and values3
    def crossdown_detected(self):
        if not self.cross12_down_ts or not self.cross13_down_ts or not self.cross23_down_ts:
            return False
        if self.cross12_down_ts < self.cross12_up_ts or self.cross13_down_ts < self.cross13_up_ts or self.cross23_down_ts < self.cross23_up_ts:
            return False
        if self.cross13_down_ts <= self.cross23_down_ts and not self.crossdown:
            self.crossdown = True
            self.crossup = False
            return True
        return False

    # detect if values1 crosses up over values2
    def cross12_up_detected(self, clear=True):
        result = False
        if self.cross12_up:
            result = True
            if clear:
                self.cross12_up = False
        return result

    # detect if values1 crossed down under values2
    def cross12_down_detected(self, clear=True):
        result = False
        if self.cross12_down:
            result = True
            if clear:
                self.cross12_down = False
        return result

    # detect if values2 crosses up over values3
    def cross23_up_detected(self, clear=True):
        result = False
        if self.cross23_up:
            result = True
            if clear:
                self.cross23_up = False
        return result

    # detect if values2 crossed down under values3
    def cross23_down_detected(self, clear=True):
        result = False
        if self.cross23_down:
            result = True
            if clear:
                self.cross23_down = False
        return result

    # detect if values1 crosses up over values3
    def cross13_up_detected(self, clear=True):
        result = False
        if self.cross13_up:
            result = True
            if clear:
                self.cross13_up = False
        return result

    # detect if values1 crossed down under values3
    def cross13_down_detected(self, clear=True):
        result = False
        if self.cross13_down:
            result = True
            if clear:
                self.cross13_down = False
        return result

    def clear(self):
        self.cross12_up = False
        self.cross12_down = False
        self.cross23_up = False
        self.cross23_down = False
        self.cross13_up = False
        self.cross13_down = False
