# Price segment definition class, and child of PriceSegment is SplitPriceSegment class
class PriceSegmentNode(object):
    MODE_SPLIT_NONE    = 0
    MODE_SPLIT3_MINMAX = 1
    MODE_SPLIT3_MAXMIN = 2
    MODE_SPLIT2_MAX    = 3
    MODE_SPLIT2_MIN    = 4
    MODE_SPLIT2_HALF   = 5

    def __init__(self, min_percent_price=1.0, min_segment_size=100, max_depth=15):
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
        self.max_depth = max_depth
        self.half_split = False
        self.parent = None
        self.seg_start = None           # start PriceSegment
        self.seg_mid = None             # mid PriceSegment
        self.seg_end = None             # end PriceSegment
        # percent change of price segment
        self.percent = 0.0
        self.depth = 0
        self.type = 0
        self.mode = PriceSegmentNode.MODE_SPLIT_NONE
        self._is_leaf = False

    def update_percent(self):
        if not self.start_price:
            return self.percent
        self.percent = round(100.0 * (self.end_price - self.start_price) / self.start_price, 2)
        return self.percent

    def is_leaf(self):
        return self._is_leaf

    def split_new(self, prices, timestamps, n=0, t=0, parent=None):
        self.parent = parent
        self.depth = n
        self.type = t

        # Too small to split into three segments, or hit max number of recursive splits, so return
        if len(prices) <= (3 * self.min_segment_size) or n == self.max_depth:
            if t == 1:
                self.parent.seg_start = None
            elif t == 2:
                self.parent.seg_mid = None
            elif t == 3:
                self.parent.seg_end = None
            return False

        self.start_price = prices[0]
        self.end_price = prices[-1]
        self.start_ts = timestamps[0]
        self.end_ts = timestamps[-1]

        prices_end_index = len(prices) - 1

        if self.parent and (self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX or
                            self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN):
            if t == 1:
                if self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
                    self.min_price_index = prices_end_index
                    self.max_price_index = prices.index(max(prices))
                elif self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN:
                    self.max_price_index = prices_end_index
                    self.min_price_index = prices.index(min(prices))
            elif t == 2:
                if self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
                    self.min_price_index = 0
                    self.max_price_index = prices_end_index
                elif self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN:
                    self.max_price_index = 0
                    self.min_price_index = prices_end_index
            elif t == 3:
                if self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
                    self.min_price_index = prices.index(min(prices))
                    self.max_price_index = 0
                elif self.parent.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN:
                    self.max_price_index = prices.index(max(prices))
                    self.min_price_index = 0

            self.min_price = prices[self.min_price_index]
            self.min_price_ts = timestamps[self.min_price_index]
            self.max_price = prices[self.max_price_index]
            self.max_price_ts = timestamps[self.max_price_index]
        elif self.parent and (self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MIN or
                              self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MAX):
            if t == 1:
                if self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MIN:
                    self.min_price_index = prices_end_index
                    self.max_price_index = prices.index(max(prices))
                elif self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MAX:
                    self.max_price_index = prices_end_index
                    self.min_price_index = prices.index(min(prices))
            elif t == 3:
                if self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MAX:
                    self.min_price_index = prices.index(min(prices))
                    self.max_price_index = 0
                elif self.parent.mode == PriceSegmentNode.MODE_SPLIT2_MIN:
                    self.max_price_index = prices.index(max(prices))
                    self.min_price_index = 0
        else:
            self.max_price = max(prices)
            self.max_price_index = prices.index(self.max_price)
            self.max_price_ts = timestamps[self.max_price_index]
            self.min_price = min(prices)
            self.min_price_index = prices.index(self.min_price)
            self.min_price_ts = timestamps[self.min_price_index]

        # if maximum price change in segment is less than min_percent_price, return
        if self.min_percent_price:
            if 100.0 * (self.max_price - self.min_price) <= self.min_percent_price * self.min_price:
                return False

        if self.max_price_ts < self.min_price_ts:
            if (prices_end_index - self.max_price_index) < self.min_segment_size:
                if self.min_price_index < self.min_segment_size:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
                else:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_MIN
            elif (prices_end_index - self.min_price_index) < self.min_segment_size:
                if self.max_price_index < self.min_segment_size:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
                else:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_MAX
            elif (self.min_price_index - self.max_price_index) < self.min_segment_size:
                self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
            else:
                self.mode = PriceSegmentNode.MODE_SPLIT3_MAXMIN
        elif self.max_price_ts > self.min_price_ts:
            if (prices_end_index - self.min_price_index) < self.min_segment_size:
                if self.max_price_index < self.min_segment_size:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
                else:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_MIN
            elif (prices_end_index - self.max_price_index) < self.min_segment_size:
                if self.min_price_index < self.min_segment_size:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
                else:
                    self.mode = PriceSegmentNode.MODE_SPLIT2_MAX
            elif (self.max_price_index - self.min_price_index) < self.min_segment_size:
                self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
            else:
                self.mode = PriceSegmentNode.MODE_SPLIT3_MINMAX

        # if 3 levels of MODE_SPLIT2_HALF, return
        #if self.mode == PriceSegmentNode.MODE_SPLIT2_HALF and n > 3:
        #    if (parent.mode == PriceSegmentNode.MODE_SPLIT2_HALF and
        #        parent.parent.mode == PriceSegmentNode.MODE_SPLIT2_HALF):
        #        return False

        self.seg_start = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
        self.seg_end = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

        if self.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN or self.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
            if self.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
                index1 = self.min_price_index
                index2 = self.max_price_index
            else:
                # self.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN
                index1 = self.max_price_index
                index2 = self.min_price_index

            self.seg_mid = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0: index1]
            start_ts_values = timestamps[0: index1]
            self.seg_start.split_new(start_price_values, start_ts_values, n + 1, 1, parent=self)

            mid_price_values = prices[index1: index2]
            mid_ts_values = timestamps[index1: index2]
            self.seg_mid.split_new(mid_price_values, mid_ts_values, n + 1, 2, parent=self)

            end_price_values = prices[index2:prices_end_index]
            end_ts_values = timestamps[index2:prices_end_index]
            self.seg_end.split_new(end_price_values, end_ts_values, n + 1, 3, parent=self)
        else:
            if self.mode == PriceSegmentNode.MODE_SPLIT2_MAX:
                index = self.max_price_index
            elif self.mode == PriceSegmentNode.MODE_SPLIT2_MIN:
                index = self.min_price_index
            else:
                # self.mode == PriceSegmentNode.MODE_SPLIT2_HALF
                index = int(prices_end_index / 2)
                if index <= self.min_segment_size:
                    return

            self.seg_mid = None

            start_price_values = prices[0:index]
            start_ts_values = timestamps[0:index]
            self.seg_start.split_new(start_price_values, start_ts_values, n+1, 1, parent=self)

            end_price_values = prices[index:prices_end_index]
            end_ts_values = timestamps[index:prices_end_index]
            self.seg_end.split_new(end_price_values, end_ts_values, n+1, 3, parent=self)


    # recursively split prices/timestamps to create tree with seg_start, seg_mid, and end_segment
    def split(self, prices, timestamps, n=0, t=0, parent=None):
        self.parent = parent
        self.depth = n
        self.type = t

        self.start_price = prices[0]
        self.end_price = prices[-1]
        self.start_ts = timestamps[0]
        self.end_ts = timestamps[-1]

        prices_end_index = len(prices) - 1

        if parent and parent.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
            if t == 1:
                self.min_price_index = prices_end_index
                self.min_price = prices[prices_end_index]
                self.min_price_ts = timestamps[prices_end_index]
                self.max_price = max(prices)
                self.max_price_index = prices.index(self.max_price)
                self.max_price_ts = timestamps[self.max_price_index]
            elif t == 2:
                self.min_price_index = 0
                self.min_price = prices[0]
                self.min_price_ts = timestamps[0]
                self.max_price_index = prices_end_index
                self.max_price = prices[prices_end_index]
                self.max_price_ts = timestamps[prices_end_index]
            elif t == 3:
                self.min_price = min(prices)
                self.min_price_index = prices.index(self.min_price)
                self.min_price_ts = timestamps[self.min_price_index]
                self.max_price_index = 0
                self.max_price = prices[0]
                self.max_price_ts = timestamps[0]
        elif parent and parent.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN:
            if t == 1:
                self.min_price = min(prices)
                self.min_price_index = prices.index(self.min_price)
                self.min_price_ts = timestamps[self.min_price_index]
                self.max_price_index = prices_end_index
                self.max_price = prices[prices_end_index]
                self.max_price_ts = timestamps[prices_end_index]
            elif t == 2:
                self.min_price_index = prices_end_index
                self.min_price = prices[prices_end_index]
                self.min_price_ts = timestamps[prices_end_index]
                self.max_price_index = 0
                self.max_price = prices[0]
                self.max_price_ts = timestamps[0]
            elif t == 3:
                self.min_price_index = 0
                self.min_price = prices[0]
                self.min_price_ts = timestamps[0]
                self.max_price = max(prices)
                self.max_price_index = prices.index(self.max_price)
                self.max_price_ts = timestamps[self.max_price_index]
        else:
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
            #if 100.0*(self.max_price - self.min_price) / self.min_price <= self.min_percent_price:
            if 100.0 * (self.max_price - self.min_price) <= self.min_percent_price * self.min_price:
                self._is_leaf = True
                return False

        # Too small to split into three segments, so return
        if len(prices) <= (3 * self.min_segment_size):
            self._is_leaf = True
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
            self._is_leaf = True
            return False

        # split prices and timestamps into two equal size parts
        if self.half_split:
            self.mode = PriceSegmentNode.MODE_SPLIT2_HALF
            mid_index = int(len(prices) / 2)
            self.seg_start = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.seg_mid = None
            self.seg_end = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0:mid_index]
            start_ts_values = timestamps[0:mid_index]
            self.seg_start.split(start_price_values, start_ts_values, n+1, 1, parent=self)

            end_price_values = prices[mid_index:-1]
            end_ts_values = timestamps[mid_index:-1]
            self.seg_end.split(end_price_values, end_ts_values, n+1, 3, parent=self)
        else:
            # split prices and timestamps into three parts
            if self.max_price_ts < self.min_price_ts:
                self.mode = PriceSegmentNode.MODE_SPLIT3_MAXMIN
                index1 = self.max_price_index
                index2 = self.min_price_index
            elif self.max_price_ts > self.min_price_ts:
                self.mode = PriceSegmentNode.MODE_SPLIT3_MINMAX
                index1 = self.min_price_index
                index2 = self.max_price_index
            else:
                self._is_leaf = True
                return False

            self.seg_start = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.seg_mid = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.seg_end = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0: index1]
            start_ts_values = timestamps[0: index1]
            self.seg_start.split(start_price_values, start_ts_values, n+1, 1, parent=self)

            mid_price_values = prices[index1: index2]
            mid_ts_values = timestamps[index1: index2]
            self.seg_mid.split(mid_price_values, mid_ts_values, n+1, 2, parent=self)

            end_price_values = prices[index2:-1]
            end_ts_values = timestamps[index2:-1]
            self.seg_end.split(end_price_values, end_ts_values, n+1, 3, parent=self)

        return True
