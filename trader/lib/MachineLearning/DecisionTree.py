from sklearn import tree
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.indicator.AEMA import AEMA

class DecisionTreeLearning(object):
    def __init__(self, win_secs=3600):
        self.clf = tree.DecisionTreeClassifier()
        self.aema12 = AEMA(12, scale_interval_secs=60)
        self.mts = MovingTimeSegment(win_secs, disable_fmm=False)
        self.lpc = LargestPriceChange()
        self.segments = None

    def ready(self):
        return self.mts.ready()

    def update(self, close, ts):
        self.aema12.update(close, ts)
        if not self.aema12.ready():
            return

        self.mts.update(self.aema12.result, ts)

        if not self.mts.ready():
            return

    def lpc_process_features(self):
        timestamps = self.mts.get_timestamps()
        start_ts = timestamps[0]
        end_ts = timestamps[-1]
        values = self.mts.get_values()

        # *TODO* determine features before running self.clf.fit()
        # determine peaks / valleys / uptrend / downtrend
        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()
        self.segments = self.lpc.get_price_segments_percent_sorted()

        dtfl = DecisionTreeFeatureList(start_ts, end_ts, len(timestamps))
        for segment in self.segments:
            dtfl.process(segment.start_ts, segment.end_ts, segment.percent)

class DecisionTreeFeatureList(object):
    def __init__(self, start_ts, end_ts, size):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.size = size
        self.feature_list = []

    def process(self, start_ts, end_ts, percent):
        if not len(self.feature_list):
            f = DecisionTreeFeature(start_ts, end_ts, percent)
            self.feature_list.append(f)
            return
        # *TODO* determine if start_ts, end_ts overlap any features in list



class DecisionTreeFeature(object):
    CLASS_NONE = 0
    CLASS_SLOW_DOWN = 1
    CLASS_SLOW_UP = 2
    CLASS_FAST_DOWN = 3
    CLASS_FAST_UP = 4
    def __init__(self, start_ts, end_ts, percent):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.percent = percent
        if percent < -1.0:
            self.class_type = DecisionTreeFeature.CLASS_FAST_DOWN
        elif -1.0 < percent < 0.0:
            self.class_type = DecisionTreeFeature.CLASS_SLOW_DOWN
        elif 0.0 <= percent < 1.0:
            self.class_type = DecisionTreeFeature.CLASS_SLOW_UP
        elif percent > 1.0:
            self.class_type = DecisionTreeFeature.CLASS_FAST_UP

    def in_range(self, ts):
        if self.start_ts <= ts <= self.end_ts:
            return True
        return False

