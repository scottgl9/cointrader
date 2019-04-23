import numpy as np
from sklearn import tree, preprocessing
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.indicator.EMA import EMA

class DecisionTree2(object):
    def __init__(self, win_secs=3600*4, clf_update_secs=1800):
        self.win_secs = win_secs
        self.clf_update_secs = clf_update_secs
        self.clf_update_ts = 0
        self.scaler = preprocessing.MinMaxScaler()
        self.mts = MovingTimeSegment(win_secs, disable_fmm=False, enable_volume=True)
        self.dtlf = None
        self.clf = None
        self.data = None
        self.ema = EMA(12, scale=24)

    def update(self, close, volume, ts):
        self.ema.update(close)
        self.mts.update(self.ema.result, ts, volume)

        if not self.mts.ready():
            return

        if not self.clf_update_ts or (ts - self.clf_update_ts) > 1000 * self.clf_update_secs:
            self.data = []
            #self.lpc_process_features()
            #self.clf_fit_labels()
            self.clf_update_ts = ts
        elif self.clf:
            pass

    def process_features(self):
        timestamps = self.mts.get_timestamps()
        values = self.mts.get_values()
        volumes = self.mts.get_volumes()
        return