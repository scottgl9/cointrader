# Fibonacci pivot points (support / resistance lines)


class Fibonacci(object):
    def __init__(self):
        self.high = 0
        self.low = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0
        self.pp = 0

    def update(self, close, low, high):
        self.low = low
        self.high = high

        self.pp = (self.high + self.low + close) / 3.0
        self.s1 = self.pp - .382 * (self.high - self.low)
        self.s2 = self.pp - .618 * (self.high - self.low)
        self.s3 = self.pp - 1 * (self.high - self.low)
        self.r1 = self.pp + .382 * (self.high - self.low)
        self.r2 = self.pp + .618 * (self.high - self.low)
        self.r3 = self.pp + 1 * (self.high - self.low)
