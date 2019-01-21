class LargestPriceChange(object):
    def __init__(self, prices=None, timestamps=None):
        self.prices = prices
        self.timestamps = timestamps
        self.root = PriceSegment(self.prices, self.timestamps)

    def divide_price_segments(self):
        self.root.split()


class SplitPriceSegment(object):
    def __init__(self, prices=None, timestamps=None, min_percent_price=1.0, min_segment_size=50):
        self.prices = prices
        self.timestamps = timestamps
        self.min_price = 0
        self.min_price_index = -1
        self.min_price_ts = 0
        self.max_price = 0
        self.max_price_index = -1
        self.max_price_ts = 0
        self.min_percent_price = min_percent_price
        self.min_segment_size = min_segment_size
        self.start_segment = None           # start PriceSegment
        self.mid_segment = None             # mid PriceSegment
        self.end_segment = None             # end PriceSegment

    def split(self):
        self.max_price = max(self.prices)
        self.max_price_index = self.prices.index(self.max_price)
        self.max_price_ts = self.timestamps[self.max_price_index]
        self.min_price = min(self.prices)
        self.min_price_index = self.prices.index(self.min_price)
        self.min_price_ts = self.timestamps[self.min_price_index]

        if 100.0*(self.max_price - self.min_price) / self.min_price <= self.min_percent_price:
            return

        if abs(self.max_price_index - self.min_price_index) < self.min_segment_size:
            return

        if self.min_price_index < self.max_price_index:
            if self.min_price_index < self.min_segment_size:
                return
            if (len(self.prices) - self.max_price_index) < self.min_segment_size:
                return
        elif self.min_price_index > self.max_price_index:
            if self.max_price_index < self.min_segment_size:
                return
            if (len(self.prices) - self.min_price_index) < self.min_segment_size:
                return
        else:
            return

        if self.max_price_ts < self.min_price_ts:
            start_price_values = self.prices[0:(self.max_price_index - 1)]
            start_ts_values = self.timestamps[0:(self.max_price_index - 1)]
            mid_price_values = self.prices[self.max_price_index:self.min_price_index]
            mid_ts_values = self.timestamps[self.max_price_index:self.min_price_index]
            end_price_values = self.prices[(self.min_price_index + 1):-1]
            end_ts_values = self.timestamps[(self.min_price_index + 1):-1]
        elif self.max_price_ts > self.min_price_ts:
            start_price_values = self.prices[0: (self.min_price_index - 1)]
            start_ts_values = self.timestamps[0: (self.min_price_index - 1)]
            mid_price_values = self.prices[self.min_price_index: self.max_price_index]
            mid_ts_values = self.timestamps[self.min_price_index: self.max_price_index]
            end_price_values = self.prices[(self.max_price_index + 1):-1]
            end_ts_values = self.timestamps[(self.max_price_index + 1):-1]
        else:
            return

        self.start_segment = PriceSegment(start_price_values, start_ts_values)
        self.mid_segment = PriceSegment(mid_price_values, mid_ts_values)
        self.end_segment = PriceSegment(end_price_values, end_ts_values)

        self.start_segment.split()
        self.mid_segment.split()
        self.end_segment.split()


class PriceSegment(object):
    def __init__(self, prices, timestamps):
        self.ts_values = timestamps
        self.price_values = prices
        self.start_ts = self.ts_values[0]
        self.end_ts = self.ts_values[-1]
        # child SplitPriceSegment class
        self.child = None

    def split(self):
        self.child = SplitPriceSegment(self.price_values, self.ts_values)
        self.child.split()
