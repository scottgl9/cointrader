# Rate of change for TimeSegmentPercentChange
from trader.lib.TimeSegmentPercentChange import TimeSegmentPercentChange
from trader.lib.TimeSegmentValues import TimeSegmentValues


class TimeSegmentPercentChangeROC(object):
    def __init__(self, tspc_seconds, roc_seconds, smoother=None):
        self.tspc_seconds = tspc_seconds
        self.roc_seconds = roc_seconds
        self.tspc = TimeSegmentPercentChange(seconds=tspc_seconds, smoother=smoother)
        self.tsv_roc = TimeSegmentValues(seconds=roc_seconds)
        self.result = 0

    def update(self, value, ts):
        self.tspc.update(value, ts)
        #if self.tspc.ready():
        pchange = self.tspc.get_percent_change()
        self.tsv_roc.update(pchange, ts)
        self.result = self.tsv_roc.diff()
        return self.result
