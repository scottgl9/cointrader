# Moving Time Segment version of ROC (Rate of Change)

class MTS_ROC(object):
    def __init__(self, win_secs=3600):
        self.win_secs = win_secs
        self.values = []
        self.seconds = []
        self.start_ts = 0
        self.result = 0
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
        while (secs - self.seconds[cnt]) > self.win_secs:
            cnt += 1

        if cnt != 0:
            self.seconds = self.seconds[cnt:]
            self.values = self.values[cnt:]
            if not self.full:
                self.full = True

        if not self.full:
            return self.result

        # this gives percent change per win_secs, by default percent change per hour
        pchange = 100.0 * (self.values[-1] - self.values[0]) / self.values[0]
        self.result = pchange

        return self.result
