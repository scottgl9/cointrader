# Estimate the cyclical behavior (a cycle consists of three points in the price data with equal price


class CycleEstimator(object):
    def __init__(self, capture_rate_secs=60):
        self.capture_rate_secs = capture_rate_secs
        self.last_capture_ts = 0
        self.time_price_index = {}
        self.price_time_index = {}

    def update(self, value, ts):
        if self.last_capture_ts and (ts - self.last_capture_ts) < self.capture_rate_secs * 1000:
            return
        self.last_capture_ts = ts
        self.time_price_index[ts] = value
        try:
            timestamps = self.price_time_index[value]
            timestamps.append(ts)
            self.price_time_index = timestamps
        except KeyError:
            self.price_time_index[value] = [ts]
