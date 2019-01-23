from trader.lib.TimeSegmentValues import TimeSegmentValues
from trader.lib.TimeSegmentPercentChange import TimeSegmentPercentChange
from trader.indicator.EMA import EMA


class TrendTrack(object):
    def __init__(self, ema1_win=12, ema2_win=50, ema3_win=200, scale=24, seconds=3600):
        self.scale=scale
        self.seconds = seconds
        self.ema1_win = ema1_win
        self.ema2_win = ema2_win
        self.ema3_win = ema3_win
        self.ema1 = EMA(self.ema1_win, scale=self.scale)
        self.ema2 = EMA(self.ema2_win, scale=self.scale)
        self.ema3 = EMA(self.ema3_win, scale=self.scale)
        self.ema1_tsv = TimeSegmentValues(seconds=self.seconds)
        self.ema2_tsv = TimeSegmentValues(seconds=self.seconds)
        self.ema3_tsv = TimeSegmentValues(seconds=self.seconds)
        self.ema1_tspc = TimeSegmentPercentChange(seconds=self.seconds, tsv=self.ema1_tsv)
        self.ema2_tspc = TimeSegmentPercentChange(seconds=self.seconds, tsv=self.ema2_tsv)
        self.ema3_tspc = TimeSegmentPercentChange(seconds=self.seconds, tsv=self.ema3_tsv)
        self.ema12_diff_tsv = TimeSegmentValues(seconds=self.seconds)
        self.ema23_diff_tsv = TimeSegmentValues(seconds=self.seconds)
        self.ema13_diff_tsv = TimeSegmentValues(seconds=self.seconds)

    def update(self, value, ts):
        self.ema1.update(value, ts)
        self.ema2.update(value, ts)
        self.ema3.update(value, ts)
        self.ema1_tspc.update(self.ema1.result, ts)
        self.ema2_tspc.update(self.ema2.result, ts)
        self.ema3_tspc.update(self.ema3.result, ts)
        self.ema12_diff_tsv.update(self.ema1.result - self.ema2.result, ts)
        self.ema13_diff_tsv.update(self.ema1.result - self.ema3.result, ts)
        self.ema23_diff_tsv.update(self.ema2.result - self.ema3.result, ts)
