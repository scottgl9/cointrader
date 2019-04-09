from .MovingTimeSegment import MovingTimeSegment
import numpy as np
from sklearn import linear_model

class MTSLinearRegression(object):
    def __init__(self, win_secs=3600, lr_update_secs=300):
        self.win_secs = win_secs
        self.lr_update_secs = lr_update_secs
        self.lr_current_ts = 0
        self.mts = MovingTimeSegment(seconds=self.win_secs, disable_fmm=True)
        self.lr = None
        self.pred_values = None
        self._updated = False

    def ready(self):
        return self.mts.ready()

    def update(self, value, ts):
        self.mts.update(value, ts)

        if not self.mts.ready():
            return

        if not self.lr or (ts - self.lr_current_ts) > 1000 * self.lr_update_secs:
            self.lr_current_ts = ts
            self.lr = linear_model.LinearRegression()
            timestamps = np.array(self.mts.get_timestamps()).reshape(-1, 1)
            values = np.array(self.mts.get_values()).reshape(-1, 1)
            self.lr.fit(timestamps, values)
            self.pred_values = self.lr.predict(timestamps).reshape(1, -1)[0].tolist()
            self._updated = True
            return

    def updated(self):
        result = self._updated
        self._updated = False
        return result

