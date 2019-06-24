# Moving Time Segment version of ROC (Rate of Change)

class MTS_ROC2(object):
    def __init__(self, win_secs=900, smoother=None):
        self.win_secs = win_secs
        self.smoother = smoother
        self.values = []
        self.seconds = []
        self.start_ts = 0
        self.result = 0
        self.last_result = 0
        self.full = False
        self.start_ts = 0

    def ready(self):
        return self.full

    def update(self, value, ts):
        if not self.start_ts:
            self.start_ts = ts

        # adjust ts to seconds from start
        secs = float(ts - self.start_ts) / 1000.0

        self.values.append(value)
        self.seconds.append(secs)

        cnt = 0
        while (secs - self.seconds[cnt]) >= self.win_secs:
            cnt += 1

        if cnt != 0:
            self.seconds = self.seconds[cnt:]
            self.values = self.values[cnt:]
            self.full = True

        if not self.full or (ts - self.start_ts) < self.win_secs * 2 * 1000:
            return self.result

        result = 100.0 * (self.values[-1] - self.values[0]) / (self.seconds[-1] - self.seconds[0])

        if self.smoother:
            self.result = self.smoother.update(result, ts)
        else:
            self.result = result

        return self.result
