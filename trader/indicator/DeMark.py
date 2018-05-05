# DeMark pivot points (support / resistance lines)


class DeMark(object):
    def __init__(self):
        self.high = 0
        self.low = 0
        self.r1 = 0
        self.s1 = 0
        self.pp = 0

    def update(self, open, close, low, high):
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
