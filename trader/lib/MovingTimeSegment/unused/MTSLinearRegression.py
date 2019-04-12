from .MovingTimeSegment import MovingTimeSegment
import numpy as np
from sklearn import linear_model

class MTSLinearRegression(object):
    def __init__(self, mts_secs=3600, lr_init_secs=3600, lr_predict_secs=300):
        self.mts_secs = mts_secs
        self.lr_init_secs = lr_init_secs
        self.lr_predict_secs = lr_predict_secs
        self.mts = MovingTimeSegment(seconds=self.mts_secs, disable_fmm=True)
        self.mts_lr = MovingTimeSegment(seconds=self.lr_predict_secs, disable_fmm=True)
        self.lr = None
        self.fitted_values = None
        self.pred_values = None
        self._updated = False
        self._lr_started = False
        self.timestamps = None
        self.init_ts = 0
        self.predict_update_ts = 0

    def ready(self):
        return self.mts.ready()

    def update(self, value, ts):
        if not self.init_ts:
            self.init_ts = ts

        self.mts.update(value, ts)

        if not self.mts.ready():
            return

        if not self._lr_started:
            if (ts - self.init_ts) > 1000 * self.lr_init_secs:
                self.lr = linear_model.LinearRegression(normalize=False)
                timestamps = np.array(self.mts.get_timestamps()).reshape(-1, 1)
                values = np.array(self.mts.get_values()).reshape(-1, 1)
                self.lr.fit(timestamps, values)
                self.fitted_values = self.lr.predict(timestamps)
                self._lr_started = True
            return

        self.mts_lr.update(value, ts)

        if not self.mts_lr.ready():
            return

        if not self.predict_update_ts or (ts - self.predict_update_ts) > 1000 * self.lr_predict_secs:
            self.predict_update_ts = ts
            timestamps = self.mts_lr.get_timestamps()
            self.pred_values = self.lr.predict(np.array(timestamps).reshape(-1, 1)).reshape(1, -1)[0]
            self._updated = True
            values = self.mts_lr.get_values()
            if max(self.pred_values) > max(values) or min(self.pred_values) < min(values):
                # recompute linear regression model
                self._lr_started = False
                return


    def get_pred_values(self):
        if not self.ready() or isinstance(self.pred_values, type(None)):
            return []
        return self.pred_values.tolist() #.reshape(1, -1)[0].tolist()

    def get_fitted_values(self):
        if not self.ready() or isinstance(self.fitted_values, type(None)):
            return []
        print(self.lr.coef_)
        return self.fitted_values.reshape(1, -1)[0].tolist()


    def updated(self):
        result = self._updated
        self._updated = False
        return result

