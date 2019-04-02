from sklearn import tree
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.indicator.AEMA import AEMA

class DecisionTreeLearning(object):
    def __init__(self, win_secs=3600):
        self.clf = tree.DecisionTreeClassifier()
        self.aema12 = AEMA(12, scale_interval_secs=60)
        self.mts = MovingTimeSegment(win_secs, disable_fmm=False)

    def ready(self):
        return self.mts.ready()

    def update(self, close, ts):
        self.aema12.update(close, ts)
        if not self.aema12.ready():
            return

        self.mts.update(self.aema12.result, ts)

        if not self.mts.ready():
            return

        timestamps = self.mts.get_timestamps()
        values = self.mts.get_values()

        # *TODO* determine features before running self.clf.fit()
        # determine peaks / valleys / uptrend / downtrend
