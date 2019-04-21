# DeMark pivot points (support / resistance lines)
from .IndicatorBase import IndicatorBase


class DeMark(IndicatorBase):
    def __init__(self):
        IndicatorBase.__init__(self, use_close=True, use_open=True, use_low=True, use_high=True)
        self.high = 0
        self.low = 0
        self.r1 = 0
        self.s1 = 0
        self.pp = 0

    def update(self, close, open=0, low=0, high=0, ts=0):
        self.low = low
        self.high = high
        if close < open:
            x = (high + (low * 2.0) + close)
        elif close > open:
            x = ((high * 2.0) + low + close)
        else: # close == open
            x = (high + low + (close * 2.0))

        self.r1 = x / 2.0 - low
        self.s1 = x / 2.0 - high
        self.pp = x / 4.0

        return self.s1, self.r1, self.pp
