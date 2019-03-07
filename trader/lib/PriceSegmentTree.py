# Class derrived from LargestPriceChange class (LPC) that I wrote which takes prices/timestamps and recursively
# builds a tree with three child nodes: start_segment, mid_segment, and end_segment


class PriceSegmentTree(object):
    def __init__(self, prices=None, timestamps=None, min_percent_price=1.0, min_segment_size=100):
        self.min_percent_price = min_percent_price
        self.min_segment_size = min_segment_size
        self.prices = None
        self.timestamps = None
        self.root = None
        self.prev_root = None
        self.start_index = 0
        self._compare_n = 0
        self._compare_t = 0
        self._compare_node1 = None
        self._compare_node2 = None

        if prices and timestamps:
            self.reset(prices, timestamps)

    def reset(self, prices, timestamps, start_index=0):
        if start_index:
            self.start_index = start_index
            self.prices = prices[self.start_index:]
            self.timestamps = timestamps[self.start_index:]
        else:
            self.prices = prices
            self.timestamps = timestamps
        self.prev_root = self.root
        self.root = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

    def split(self):
        self.root.split(self.prices, self.timestamps)

    def compare(self, node1=None, node2=None, n=0, t=None):
        if not t:
            t = []
            if not node1:
                if not self.prev_root:
                    return
                node1 = self.prev_root
            if not node2:
                node2 = self.root

        if node1.start_ts != node2.start_ts or node1.end_ts != node2.end_ts:
            self._compare_n = n
            self._compare_t = t
            self._compare_node1 = node1
            self._compare_node2 = node2
            return

        if node1.start_segment and node2.start_segment:
            self.compare(node1.start_segment, node2.start_segment, n+1, t.append(1))

        if node1.mid_segment and node2.mid_segment:
            self.compare(node1.start_segment, node2.start_segment, n+1, t.append(2))

        if node1.end_segment and node2.end_segment:
            self.compare(node1.end_segment, node2.end_segment, n+1, t.append(3))

    def get_compare_results(self):
        return {'n': self._compare_n, 't': self._compare_t, 'node1': self._compare_node1, 'node2': self._compare_node2}


# Price segment definition class, and child of PriceSegment is SplitPriceSegment class
class PriceSegmentNode(object):
    def __init__(self, min_percent_price=1.0, min_segment_size=100):
        self.start_price = 0
        self.end_price = 0
        self.start_ts = 0
        self.end_ts = 0
        self.min_price = 0
        self.min_price_index = -1
        self.min_price_ts = 0
        self.max_price = 0
        self.max_price_index = -1
        self.max_price_ts = 0
        self.min_percent_price = min_percent_price
        self.min_segment_size = min_segment_size
        self.half_split = False
        self.start_segment = None           # start PriceSegment
        self.mid_segment = None             # mid PriceSegment
        self.end_segment = None             # end PriceSegment
        # percent change of price segment
        self.percent = 0.0

    # recursively split prices/timestamps to create tree with start_segment, mid_segment, and end_segment
    def split(self, prices, timestamps):
        self.start_price = prices[0]
        self.end_price = prices[-1]
        self.start_ts = timestamps[0]
        self.end_ts = timestamps[-1]
        self.percent = round(100.0 * (self.end_price - self.start_price) / self.start_price, 2)

        self.max_price = max(prices)
        self.max_price_index = prices.index(self.max_price)
        self.max_price_ts = timestamps[self.max_price_index]
        self.min_price = min(prices)
        self.min_price_index = prices.index(self.min_price)
        self.min_price_ts = timestamps[self.min_price_index]

        #diff_secs = (timestamps[-1] - timestamps[0])
        #if diff_secs <= self.min_segment_seconds * 1000 * 3:
        #    return False

        # if maximum price change in segment is less than min_percent_price, return
        if self.min_percent_price:
            if 100.0*(self.max_price - self.min_price) / self.min_price <= self.min_percent_price:
                return False

        # Too small to split into three segments, so return
        if len(prices) <= (3 * self.min_segment_size):
            return False

        # if mid segment size is less than min_segment_size, set half_split mode
        if abs(self.max_price_index - self.min_price_index) < self.min_segment_size:
            self.half_split = True

        # if start or end segment size is less than min_segment_size, set half_split mode
        if self.min_price_index < self.max_price_index:
            if self.min_price_index < self.min_segment_size:
                self.half_split = True
            if (len(prices) - self.max_price_index) < self.min_segment_size:
                self.half_split = True
        elif self.min_price_index > self.max_price_index:
            if self.max_price_index < self.min_segment_size:
                self.half_split = True
            if (len(prices) - self.min_price_index) < self.min_segment_size:
                self.half_split = True
        else:
            return False

        # split prices and timestamps into two equal size parts
        if self.half_split:
            mid_index = int(len(prices) / 2)
            start_price_values = prices[0:mid_index]
            start_ts_values = timestamps[0:mid_index]
            end_price_values = prices[mid_index:-1]
            end_ts_values = timestamps[mid_index:-1]
            self.start_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.mid_segment = None
            self.end_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            self.start_segment.split(start_price_values, start_ts_values)
            self.end_segment.split(end_price_values, end_ts_values)
        else:
            # split prices and timestamps into three parts
            if self.max_price_ts < self.min_price_ts:
                start_price_values = prices[0:(self.max_price_index - 1)]
                start_ts_values = timestamps[0:(self.max_price_index - 1)]
                mid_price_values = prices[self.max_price_index:self.min_price_index]
                mid_ts_values = timestamps[self.max_price_index:self.min_price_index]
                end_price_values = prices[(self.min_price_index + 1):-1]
                end_ts_values = timestamps[(self.min_price_index + 1):-1]
            elif self.max_price_ts > self.min_price_ts:
                start_price_values = prices[0: (self.min_price_index - 1)]
                start_ts_values = timestamps[0: (self.min_price_index - 1)]
                mid_price_values = prices[self.min_price_index: self.max_price_index]
                mid_ts_values = timestamps[self.min_price_index: self.max_price_index]
                end_price_values = prices[(self.max_price_index + 1):-1]
                end_ts_values = timestamps[(self.max_price_index + 1):-1]
            else:
                return False

            self.start_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.mid_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.end_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            self.start_segment.split(start_price_values, start_ts_values)
            self.mid_segment.split(mid_price_values, mid_ts_values)
            self.end_segment.split(end_price_values, end_ts_values)

        return True
