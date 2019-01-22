class LargestPriceChange(object):
    def __init__(self, prices=None, timestamps=None):
        self.prices = prices
        self.timestamps = timestamps
        self.root = PriceSegment(self.prices, self.timestamps)
        self.ts_segments = {}

    def divide_price_segments(self):
        self.root.split()

    def print_price_segments(self, node=None):
        if not node:
            node = self.root
        if not node.child:
            return

        start_price = node.price_values[0]
        end_price = node.price_values[-1]
        start_ts = node.ts_values[0]
        end_ts = node.ts_values[-1]
        #print(start_ts, end_ts)

        if node.child.start_segment:
            self.print_price_segments(node.child.start_segment)
        if node.child.mid_segment:
            self.print_price_segments(node.child.mid_segment)
        if node.child.end_segment:
            self.print_price_segments(node.child.end_segment)

    def get_timestamp_segments(self):
        self.ts_segments = {}
        self.timestamp_segments()
        return self.ts_segments

    def timestamp_segments(self, node=None, level=1):
        if not node:
            node = self.root
        if not node.child:
            return

        start_ts = node.ts_values[0]
        end_ts = node.ts_values[-1]

        if start_ts not in self.ts_segments.keys():
            self.ts_segments[start_ts] = 1
        if end_ts not in self.ts_segments.keys():
            self.ts_segments[end_ts] = -1

        if node.child.start_segment:
            self.timestamp_segments(node.child.start_segment, level=level+1)
        if node.child.mid_segment:
            self.timestamp_segments(node.child.mid_segment, level=level+1)
        if node.child.end_segment:
            self.timestamp_segments(node.child.end_segment, level=level+1)


# Class to handle splitting a price segment into three parts
class SplitPriceSegment(object):
    def __init__(self, prices=None, timestamps=None, min_percent_price=1.0, min_segment_size=100):
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

        # if maximum price change in segment is less than min_percent_price, return
        if 100.0*(self.max_price - self.min_price) / self.min_price <= self.min_percent_price:
            return

        # Too small to split into three segments, so return
        if len(self.prices) <= (3 * self.min_segment_size):
            return

        half_split = False

        # if mid segment size is less than min_segment_size, set half_split mode
        if abs(self.max_price_index - self.min_price_index) < self.min_segment_size:
            half_split = True

        # if start or end segment size is less than min_segment_size, set half_split mode
        if self.min_price_index < self.max_price_index:
            if self.min_price_index < self.min_segment_size:
                half_split = True
            if (len(self.prices) - self.max_price_index) < self.min_segment_size:
                half_split = True
        elif self.min_price_index > self.max_price_index:
            if self.max_price_index < self.min_segment_size:
                half_split = True
            if (len(self.prices) - self.min_price_index) < self.min_segment_size:
                half_split = True
        else:
            return

        if half_split:
            mid_index = int(len(self.prices) / 2)
            start_price_values = self.prices[0:mid_index]
            start_ts_values = self.timestamps[0:mid_index]
            end_price_values = self.prices[mid_index:-1]
            end_ts_values = self.timestamps[mid_index:-1]
            self.mid_segment = None
            self.start_segment = PriceSegment(start_price_values, start_ts_values)
            self.end_segment = PriceSegment(end_price_values, end_ts_values)

            self.start_segment.split()
            self.end_segment.split()
        else:
            # split self.prices and self.timestamps into three parts
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


# Price segment definition class, and child of PriceSegment is SplitPriceSegment class
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
