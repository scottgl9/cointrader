# Estimate the cyclical behavior (a cycle consists of three points in the price data with equal price


class CycleEstimator(object):
    def __init__(self, capture_rate_secs=60):
        self.capture_rate_secs = capture_rate_secs
        self.last_capture_ts = 0
        self.time_price_index = {}
        self.price_time_index = {}
        self.price_count_index = {}
        self.count_price_ge3_index = []
        self.cycle_found = False

    def update(self, value, ts):
        if self.last_capture_ts and (ts - self.last_capture_ts) < self.capture_rate_secs * 1000:
            return
        self.last_capture_ts = ts
        self.time_price_index[ts] = value
        try:
            if not self.price_time_index[value]:
                self.price_time_index[value] = [ts]
            else:
                self.price_time_index[value].append(ts)
        except KeyError:
            self.price_time_index[value] = [ts]

        try:
            count = self.price_count_index[value] + 1
            if count >= 3:
                self.cycle_found = True
                if value not in self.count_price_ge3_index:
                    self.count_price_ge3_index.append(value)
            self.price_count_index[value] = count
        except KeyError:
            self.price_count_index[value] = 1

    def get_trade_range(self):
        if not self.cycle_found:
            return 0, 0
        return min(self.count_price_ge3_index), max(self.count_price_ge3_index)
