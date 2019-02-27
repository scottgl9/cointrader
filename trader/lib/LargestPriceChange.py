class LargestPriceChange(object):
    def __init__(self, prices=None, timestamps=None, use_dict=False):
        self.use_dict = use_dict
        self.prices = None
        self.timestamps = None
        self.root = None
        self._price_segment_percents = None
        self.start_index = 0
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
        self.root = PriceSegment(self.prices, self.timestamps)
        self._price_segment_percents = []

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

    def get_price_segment_percents(self):
        self._price_segment_percents = []
        self.price_segment_percents(node=self.root)
        # sort by percent
        if self.use_dict:
            self._price_segment_percents.sort(key=lambda x: x['percent'])
        else:
            self._price_segment_percents.sort()
        return self._price_segment_percents

    # return largest negative price change, and largest positive price change
    def get_largest_price_segment_percents(self):
        price_segment_percents = self.get_price_segment_percents()
        return [price_segment_percents[0], price_segment_percents[-1]]

    def price_segment_percents(self, node=None, n=1):
        if not node:
            node = self.root

        if self.use_dict:
            self._price_segment_percents.append({'percent': float(node.percent),
                                                 'start_ts': int(node.start_ts),
                                                 'end_ts': int(node.end_ts)})
        else:
            self._price_segment_percents.append(LPCSegment(node.percent, node.start_ts, node.end_ts))

        if not node.child:
            return

        if node.child.start_segment:
            self.price_segment_percents(node.child.start_segment, n=n+1)
        if node.child.mid_segment:
            self.price_segment_percents(node.child.mid_segment, n=n+1)
        if node.child.end_segment:
            self.price_segment_percents(node.child.end_segment, n=n+1)


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
            return False

        # Too small to split into three segments, so return
        if len(self.prices) <= (3 * self.min_segment_size):
            return False

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
            return False

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
                return False

            self.start_segment = PriceSegment(start_price_values, start_ts_values)
            self.mid_segment = PriceSegment(mid_price_values, mid_ts_values)
            self.end_segment = PriceSegment(end_price_values, end_ts_values)

            self.start_segment.split()
            self.mid_segment.split()
            self.end_segment.split()

        return True


# Price segment definition class, and child of PriceSegment is SplitPriceSegment class
class PriceSegment(object):
    def __init__(self, prices, timestamps):
        self.ts_values = timestamps
        self.price_values = prices
        #self.max_price = max(self.price_values)
        #self.max_price_index = self.price_values.index(self.max_price)
        #self.max_price_ts = self.ts_values[self.max_price_index]
        #self.min_price = min(self.price_values)
        #self.min_price_index = self.price_values.index(self.min_price)
        #self.min_price_ts = self.ts_values[self.min_price_index]
        self.start_price = self.price_values[0]
        self.end_price = self.price_values[-1]
        self.start_ts = self.ts_values[0]
        self.end_ts = self.ts_values[-1]

        # percent change of price segment
        self.percent = round(100.0 * (self.end_price - self.start_price) / self.start_price, 2)

        # child SplitPriceSegment class
        self.child = None

    def split(self):
        self.child = SplitPriceSegment(self.price_values, self.ts_values)

        # if failed to split, self self.child=None
        if not self.child.split():
            self.child = None


class LPCSegment(object):
    def __init__(self, percent=0, start_ts=0, end_ts=0):
        self.start_ts = int(start_ts)
        self.end_ts = int(end_ts)
        self.percent = float(percent)

    def __getitem__(self, item):
        if item == 'start_ts':
            return int(self.start_ts)
        elif item == 'end_ts':
            return int(self.end_ts)
        elif item == 'percent':
            return float(self.percent)

    def __lt__(self, other):
        if self.percent < other.percent:
            return True
        return False

    def __repr__(self):
        return str(self.__dict__())

    def __dict__(self):
        return {'start_ts': self.start_ts, 'end_ts': self.end_ts, 'percent': self.percent}

