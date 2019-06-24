# Supertrend Indicator
# http://www.freebsensetips.com/blog/detail/7/What-is-supertrend-indicator-its-calculation
#  BASIC UPPERBAND  =  (HIGH + LOW) / 2 + Multiplier * ATR
#  BASIC LOWERBAND =  (HIGH + LOW) / 2 - Multiplier * ATR
#  FINAL UPPERBAND = IF( (Current BASICUPPERBAND  < Previous FINAL UPPERBAND) and (Previous Close > Previous FINAL UPPERBAND)) THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
#  FINAL LOWERBAND = IF( (Current BASIC LOWERBAND  > Previous FINAL LOWERBAND) and (Previous Close < Previous FINAL LOWERBAND)) THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)
#  SUPERTREND = IF(Current Close <= Current FINAL UPPERBAND ) THEN Current FINAL UPPERBAND ELSE Current  FINAL LOWERBAND

from .IndicatorBase import IndicatorBase
from .ATR import ATR


class Supertrend(IndicatorBase):
    def __init__(self, window=14, multiplier=4):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.window = window
        self.multiplier = multiplier
        self.atr = ATR(window)
        self.basic_ub = 0
        self.basic_lb = 0
        self.final_ub = 0
        self.final_lb = 0
        self.prev_final_ub = 0
        self.prev_final_lb = 0
        self.prev_close = 0
        self.result = 0

    def update(self, close, low, high):
        self.atr.update(close, low, high)
        if not self.atr.result:
            self.prev_close = close
            return self.result

        self.basic_ub = (high + low) / 2.0 + self.multiplier * self.atr.result
        self.basic_lb = (high + low) / 2.0 - self.multiplier * self.atr.result

        self.prev_final_ub = self.final_ub
        self.prev_final_lb = self.final_lb

        if self.basic_ub < self.prev_final_ub < self.prev_close:
            self.final_ub = self.basic_ub
        else:
            self.final_ub = self.prev_final_ub

        if self.basic_lb > self.prev_final_lb > self.prev_close:
            self.final_lb = self.basic_lb
        else:
            self.final_lb = self.prev_final_lb

        if close <= self.final_ub:
            self.result = self.final_ub
        else:
            self.result = self.final_lb

        return self.result
