from sklearn import tree
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.LargestPriceChange import LargestPriceChange
from trader.indicator.AEMA import AEMA

class DecisionTreeLearning(object):
    def __init__(self, win_secs=3600, lpc_update_secs=300, clf_update_secs=1800):
        self.win_secs = win_secs
        self.lpc_update_secs = lpc_update_secs
        self.clf_update_secs = clf_update_secs
        self.lpc_update_ts = 0
        self.clf_update_ts = 0
        self.clf = tree.DecisionTreeClassifier()
        self.aema12 = AEMA(12, scale_interval_secs=60)
        self.mts = MovingTimeSegment(win_secs, disable_fmm=False)
        self.lpc = LargestPriceChange()
        self.dtfl = None
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

        if not self.lpc_update_ts or (ts - self.lpc_update_ts) > 1000 * self.lpc_update_secs:
            self.lpc_update_segments()
            self.lpc_update_ts = ts

        if not self.clf_update_ts or (ts - self.clf_update_ts) > 1000 * self.clf_update_secs:
            self.lpc_process_features()
            self.clf_fit_labels()

    def lpc_update_segments(self):
        timestamps = self.mts.get_timestamps()
        values = self.mts.get_values()

        self.lpc.reset(values, timestamps)
        self.lpc.divide_price_segments()
        self.segments = self.lpc.get_price_segments_percent_sorted()

    def lpc_process_features(self):
        timestamps = self.mts.get_timestamps()
        start_ts = timestamps[0]
        end_ts = timestamps[-1]

        self.dtfl = DecisionTreeFeatureList(start_ts, end_ts, timestamps)
        for segment in self.segments:
            self.dtfl.process(segment.start_ts, segment.end_ts, segment.start_price, segment.end_price, segment.percent)
        self.dtfl.sort()

    def clf_fit_labels(self):
        values = self.mts.get_values()
        labels = self.dtfl.labels()
        self.clf.fit(values, labels)


class DecisionTreeFeatureList(object):
    def __init__(self, start_ts, end_ts, timestamps):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.timestamps = timestamps
        self.feature_list = []
        self._labels = len(self.timestamps) * [DecisionTreeFeature.CLASS_NONE]

    def reset(self, start_ts, end_ts, timestamps):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.timestamps = timestamps
        self.feature_list = []
        self._labels = len(self.timestamps) * [DecisionTreeFeature.CLASS_NONE]

    def labels(self):
        for f in self.feature_list:
            start_index = self.timestamps.index(f.start_ts)
            end_index = self.timestamps.index(f.end_ts)
            for i in range(start_index, end_index):
                self._labels[i] = f.class_type
        return self._labels

    def sort(self):
        self.feature_list.sort(key=lambda x: x.start_ts)

    def process(self, start_ts, end_ts, start_price, end_price, percent):
        if not len(self.feature_list):
            f = DecisionTreeFeature(start_ts, end_ts, start_price, end_price, percent)
            self.feature_list.append(f)
            return

        new_feature = True
        start_index = -1
        end_index = -1
        for f in self.feature_list:
            # total feature is within existing feature, ignore
            if f.in_range(start_ts) and f.in_range(end_ts):
                return
            # feature overlaps existing feature range
            elif f.in_range(start_ts):
                new_feature = False
                start_index = self.feature_list.index(f)
            elif f.in_range(end_ts):
                new_feature = False
                end_index = self.feature_list.index(f)

        if new_feature:
            f = DecisionTreeFeature(start_ts, end_ts, start_price, end_price, percent)
            self.feature_list.append(f)
        else:
            # new feature start occurs within existing feature
            if start_index != -1 and end_index == -1:
                f1 = self.feature_list[start_index]
                f2 = DecisionTreeFeature(start_ts, end_ts, start_price, end_price, percent)
                if f1.class_type == f2.class_type:
                    self.feature_list[start_index].end_ts = end_ts
                    self.feature_list[start_index].end_price = end_price
                    self.feature_list[start_index].update_percent()
                    self.feature_list[start_index].update_class_type()
                else:
                    f2.start_ts = f1.end_ts
                    f2.start_price = f2.end_price
                    f2.update_percent()
                    f2.update_class_type()
                    self.feature_list.append(f2)
            # new feature end occurs within existing feature
            elif start_index == -1 and end_index != -1:
                f1 = self.feature_list[end_index]
                f2 = DecisionTreeFeature(start_ts, end_ts, start_price, end_price, percent)
                if f1.class_type == f2.class_type:
                    self.feature_list[end_index].start_ts = start_ts
                    self.feature_list[end_index].start_price = start_price
                    self.feature_list[end_index].update_percent()
                    self.feature_list[end_index].update_class_type()
                else:
                    f2.end_ts = f1.start_ts
                    f2.end_price = f2.start_price
                    f2.update_percent()
                    f2.update_class_type()
                    self.feature_list.append(f2)

class DecisionTreeFeature(object):
    CLASS_NONE = 0
    CLASS_FLAT = 1
    CLASS_SLOW_DOWN = 2
    CLASS_SLOW_UP = 3
    CLASS_FAST_DOWN = 4
    CLASS_FAST_UP = 5
    def __init__(self, start_ts, end_ts, start_price, end_price, percent):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.start_price = start_price
        self.end_price = end_price
        self.percent = percent
        self.class_type = DecisionTreeFeature.CLASS_NONE
        self.update_class_type()

    def in_range(self, ts):
        if self.start_ts <= ts <= self.end_ts:
            return True
        return False

    def update_percent(self):
        if not self.start_price:
            return self.percent
        self.percent = round(100.0 * (self.end_price - self.start_price) / self.start_price, 2)
        return self.percent

    def update_class_type(self):
        if self.percent < -1.0:
            self.class_type = DecisionTreeFeature.CLASS_FAST_DOWN
        elif -1.0 < self.percent < 0.2:
            self.class_type = DecisionTreeFeature.CLASS_SLOW_DOWN
        elif -0.2 <= self.percent < 0.2:
            self.class_type = DecisionTreeFeature.CLASS_FLAT
        elif 0.2 <= self.percent < 1.0:
            self.class_type = DecisionTreeFeature.CLASS_SLOW_UP
        elif self.percent > 1.0:
            self.class_type = DecisionTreeFeature.CLASS_FAST_UP
