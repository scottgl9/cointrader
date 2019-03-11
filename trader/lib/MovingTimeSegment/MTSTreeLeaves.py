# Utilizes MovingTimeSegment (MTS) and PriceSegmentTree (PST) classes and tracks leaf nodes of tree
from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment
from trader.lib.PriceSegmentTree import PriceSegmentTree, PriceSegmentNode


class MTSTreeLeaves(object):
    def __init__(self, mts_seconds=3600*12, pst_start_seconds=3600, pst_update_seconds=300, smoother=None):
        self.mts_seconds = mts_seconds
        self.pst_start_seconds = pst_start_seconds
        self.pst_update_seconds = pst_update_seconds
        self.smoother = smoother
        self.mts = MovingTimeSegment(seconds=self.mts_seconds, value_smoother=self.smoother, disable_fmm=True)
        self.pst = PriceSegmentTree()
        self.pst_leaf_nodes = None
        self.start_ts = 0
        self.start_interval_ts = 0
        self._ready = False
        self._tree_updated = False

    def ready(self):
        return self._ready

    def update(self, value, ts):
        if not self.start_ts:
            self.start_ts = ts
        self.mts.update(value, ts)

        if not self._ready:
            if 1000 * (ts - self.start_ts) >= self.pst_start_seconds:
                self._ready = True
            else:
                return

        if not self.start_interval_ts:
            self.start_interval_ts = ts
        elif 1000 * (ts - self.start_interval_ts) < self.pst_update_seconds:
            self._tree_updated = False
            return

        self.pst.reset(self.mts.values, self.mts.timestamps)
        self.pst.split()
        self.pst_leaf_nodes = self.pst.get_leaf_nodes()
        self.start_interval_ts = ts
        self._tree_updated = True

    def tree_updated(self):
        return self._tree_updated

    def leaves(self):
        return self.pst_leaf_nodes
