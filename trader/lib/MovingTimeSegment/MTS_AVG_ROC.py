class MTS_AVG_ROC(object):
    def __init__(self, win_secs=300):
        self.win_secs = win_secs
        self.rocs = []
        self.timestamps = []
        self._roc_sum = 0
        self._full = False
        self.last_value = 0
        self.last_ts = 0
        self.result = 0

    def ready(self):
        return self._full

    def update(self, value, ts):
        if not self.last_ts:
            self.last_ts = ts
            self.last_value = value
            return self.result

        self.timestamps.append(ts)
        roc = (value - self.last_value) / ((ts - self.last_ts) / 1000.0)
        self._roc_sum += roc
        self.rocs.append(roc)

        cnt = 0
        for i in range(0, len(self.timestamps)):
            tss = self.timestamps[i]
            if (ts - tss) < self.win_secs * 1000:
                break
            roc = self.rocs[i]
            self._roc_sum -= roc
            cnt += 1

        if cnt:
            self.rocs = self.rocs[cnt:]
            self.timestamps = self.timestamps[cnt:]
            self._full = True

        if self._full:
            self.result = self._roc_sum / len(self.rocs)
        return self.result
