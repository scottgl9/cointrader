
class StatTracker(object):
    def __init__(self):
        self.last_close_price_30min_low = 0
        self.last_close_price_30min_high = 0
        self.close_price_30min_low = 0
        self.close_price_30min_low_ts = 0
        self.close_price_30min_high = 0
        self.close_price_30min_high_ts = 0
        self.last_close_price_1hr_low = 0
        self.last_close_price_1hr_high = 0
        self.close_price_1hr_low = 0
        self.close_price_1hr_low_ts = 0
        self.close_price_1hr_high = 0
        self.close_price_1hr_high_ts = 0
        self.last_close_price_4hr_low = 0
        self.last_close_price_4hr_high = 0
        self.close_price_4hr_low = 0
        self.close_price_4hr_low_ts = 0
        self.close_price_4hr_high = 0
        self.close_price_4hr_high_ts = 0
        self.close_price_all_low = 0
        self.close_price_all_high = 0

    def update(self, close, ts):
        if (self.close_price_30min_low_ts != 0 and
                (ts - self.close_price_30min_low_ts) / 60 >= 30):
            self.last_close_price_30min_low = self.close_price_30min_low
            self.close_price_30min_low = close
            self.close_price_30min_low_ts = ts

        if (self.close_price_30min_high_ts != 0 and
                (ts - self.close_price_30min_high_ts) / 60 >= 30):
            self.last_close_price_30min_high = self.close_price_30min_high
            self.close_price_30min_high = close
            self.close_price_30min_high_ts = ts

        if (self.close_price_1hr_low_ts != 0 and
                (ts - self.close_price_1hr_low_ts) / 60 >= 60):
            self.last_close_price_1hr_low = self.close_price_1hr_low
            self.close_price_1hr_low = close
            self.close_price_1hr_low_ts = ts

        if (self.close_price_1hr_high_ts != 0 and
                (ts - self.close_price_1hr_high_ts) / 60 >= 60):
            self.last_close_price_1hr_high = self.close_price_1hr_high
            self.close_price_1hr_high = close
            self.close_price_1hr_high_ts = ts

        if (self.close_price_4hr_low_ts != 0 and
                (ts - self.close_price_4hr_low_ts) / 60 >= 240):
            self.last_close_price_4hr_low = self.close_price_4hr_low
            self.close_price_4hr_low = close
            self.close_price_4hr_low_ts = ts

        if (self.close_price_4hr_high_ts != 0 and
                (ts - self.close_price_4hr_high_ts) / 60 >= 240):
            self.last_close_price_4hr_high = self.close_price_4hr_high
            self.close_price_4hr_high = close
            self.close_price_4hr_high_ts = ts

        if self.close_price_30min_low == 0 or close < self.close_price_30min_low:
            self.close_price_30min_low = close
            self.close_price_30min_low_ts = ts
        if self.close_price_30min_high == 0 or close > self.close_price_30min_high:
            self.close_price_30min_high = close
            self.close_price_30min_high_ts = ts
        if self.close_price_1hr_low == 0 or close < self.close_price_1hr_low:
            self.close_price_1hr_low = close
            self.close_price_1hr_low_ts = ts
        if self.close_price_1hr_high == 0 or close > self.close_price_1hr_high:
            self.close_price_1hr_high = close
            self.close_price_1hr_high_ts = ts
        if self.close_price_4hr_low == 0 or close < self.close_price_4hr_low:
            self.close_price_4hr_low = close
            self.close_price_4hr_low_ts = ts
        if self.close_price_4hr_high == 0 or close > self.close_price_4hr_high:
            self.close_price_4hr_high = close
            self.close_price_4hr_high_ts = ts
        if self.close_price_all_low == 0 or close < self.close_price_all_low:
            self.close_price_all_low = close
        if self.close_price_all_high == 0 or close > self.close_price_all_high:
            self.close_price_all_high = close

    def price_range_30min(self):
        return self.close_price_30min_low, self.close_price_30min_high

    def price_range_1hr(self):
        return self.close_price_1hr_low, self.close_price_1hr_high

    def price_range_4hr(self):
        return self.close_price_4hr_low, self.close_price_4hr_high

    def price_range_all(self):
        return self.close_price_all_low, self.close_price_all_high

    def trending_downward(self):
        if self.last_close_price_1hr_low == 0 or self.last_close_price_1hr_high == 0:
            return True

        if self.close_price_1hr_low <= self.last_close_price_1hr_low or self.close_price_1hr_high <= self.last_close_price_1hr_high:
            return True
        return False

    def trending_upward(self):
        if self.last_close_price_1hr_low == 0 or self.last_close_price_1hr_high == 0:
            return False

        if self.close_price_1hr_low > self.last_close_price_1hr_low and self.close_price_1hr_high > self.last_close_price_1hr_high:
            return True

        return False
