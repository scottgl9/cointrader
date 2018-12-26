class MADiff(object):
    def __init__(self, ma1=None, ma2=None):
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.result = 0
        self._ready = False
        self.max_diff = 0
        self.max_diff_ts = 0

    def ready(self):
        return self._ready

    def update(self, value, ts, ma1_result=0, ma2_result=0):
        if self.ma1:
            self.ma1.update(value)
            self.ma1_result = self.ma1.result
        else:
            self.ma1_result = ma1_result

        if self.ma2:
            self.ma2.update(value)
            self.ma2_result = self.ma2.result
        else:
            self.ma2_result = ma2_result

        if self.ma1_result and self.ma2_result:
            self.result = self.ma1_result - self.ma2_result
            self._ready = True
            if self.result > self.max_diff:
                self.max_diff = self.result
                self.max_diff_ts = ts

        return self.result

    def get_diff(self):
        if not self.ready():
            return 0

        return self.result

    def get_max_diff(self):
        return self.max_diff

    # get diff between max diff and current diff
    def get_max_current_diff(self):
        if not self.ready():
            return 0

        if self.max_diff != 0 and self.result != 0:
            return self.max_diff - self.result

        return 0
