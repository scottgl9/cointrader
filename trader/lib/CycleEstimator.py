# Estimate the cyclical behavior (a cycle consists of three points in the price data with equal price


class CycleEstimator(object):
    def __init__(self):
        pass

    def update(self, value, ts):
        pass

class CyclePoint(object):
    def __init__(self, value, ts):
        self.value = value
        self.ts = ts
