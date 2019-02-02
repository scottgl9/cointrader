# get MTS_SMA of small segment (ex. 1m). Then MovingTimeSegment (ex. 30m) of MTS_SMA(1m).
# newest value of MTS(MTS_SMA(1m), 30m) minus oldest value of TS(MTS_SMA(1m), 30m) is the movement rate
from .MTS_SMA import MTS_SMA
from .MovingTimeSegment import MovingTimeSegment


class MTSMoveRate(object):
    def __init__(self, small_seg_seconds=60, large_seg_seconds=3600):
        self.small_seg_seconds = small_seg_seconds
        self.large_seg_seconds = large_seg_seconds
        self.small_mts_sma = MTS_SMA(seconds=self.small_seg_seconds)
        self.large_mts = MovingTimeSegment(seconds=self.large_seg_seconds, disable_fmm=True)
        self.large_mts_first_value = 0
        self.large_mts_last_value = 0
        self.result = 0

    def update(self, value, ts):
        self.small_mts_sma.update(value, ts)
        self.large_mts.update(self.small_mts_sma.result, ts)
        self.large_mts_first_value = self.large_mts.first_value()
        self.large_mts_last_value = self.large_mts.last_value()
        self.result = self.large_mts_last_value - self.large_mts_first_value
        return self.result
