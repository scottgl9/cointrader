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
        self._leaf_nodes = []
        self._node_depth_dict = {}
        self._compare_n = 0
        self._compare_t = 0
        self._compare_node1 = None
        self._compare_node2 = None
        self._compare_done = False

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

    def get_leaf_nodes(self):
        self._leaf_nodes = []
        self._walk_leaf_nodes(self.root)
        return self._leaf_nodes

    def _walk_leaf_nodes(self, node):
        if node.is_leaf():
            node.update_percent()
            self._leaf_nodes.append(node)
            return

        if node.start_segment:
            self._walk_leaf_nodes(node.start_segment)

        if node.mid_segment:
            self._walk_leaf_nodes(node.mid_segment)

        if node.end_segment:
            self._walk_leaf_nodes(node.end_segment)

    # returns dict with list of nodes referenced by depth
    def get_nodes_by_depth(self):
        self._node_depth_dict = {}
        self._walk_node_depth_dict(self.root)
        return self._node_depth_dict

    # used by get_nodes_by_depth
    def _walk_node_depth_dict(self, node, n=0):
        if n:
            node.update_percent()
            if n in self._node_depth_dict:
                if node not in self._node_depth_dict[n]:
                    self._node_depth_dict[n].append(node)
            else:
                self._node_depth_dict[n] = [node]

        if node.start_segment:
            self._walk_node_depth_dict(node.start_segment, n+1)

        if node.mid_segment:
            self._walk_node_depth_dict(node.mid_segment, n+1)

        if node.end_segment:
            self._walk_node_depth_dict(node.end_segment, n+1)

    def compare_reset(self):
        self._compare_n = 0
        self._compare_t = None
        self._compare_node1 = None
        self._compare_node2 = None
        self._compare_done = False

    def compare(self, node1, node2, n=0, t=None):
        if self._compare_done:
            return

        if node1.start_ts != node2.start_ts: # or node1.end_ts != node2.end_ts:
            self._compare_n = n
            self._compare_t = t
            self._compare_node1 = node1
            self._compare_node2 = node2
            self._compare_done = True
            return

        if node1.start_segment and node2.start_segment:
            tnext = t
            tnext.append(1)
            self.compare(node1.start_segment, node2.start_segment, n + 1, tnext)

        if node1.mid_segment and node2.mid_segment:
            tnext = t
            tnext.append(2)
            self.compare(node1.mid_segment, node2.mid_segment, n + 1, tnext)

        if node1.end_segment and node2.end_segment:
            tnext = t
            tnext.append(3)
            self.compare(node1.end_segment, node2.end_segment, n + 1, tnext)

    def get_compare_results(self):
        return {'n': self._compare_n, 't': self._compare_t, 'node1': self._compare_node1, 'node2': self._compare_node2}


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
        self.start_segment = None           # start PriceSegment
        self.mid_segment = None             # mid PriceSegment
        self.end_segment = None             # end PriceSegment
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
                self.parent.start_segment = None
            elif t == 2:
                self.parent.mid_segment = None
            elif t == 3:
                self.parent.end_segment = None
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

        self.start_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
        self.end_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

        if self.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN or self.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
            if self.mode == PriceSegmentNode.MODE_SPLIT3_MINMAX:
                index1 = self.min_price_index
                index2 = self.max_price_index
            else:
                # self.mode == PriceSegmentNode.MODE_SPLIT3_MAXMIN
                index1 = self.max_price_index
                index2 = self.min_price_index

            self.mid_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0: index1]
            start_ts_values = timestamps[0: index1]
            self.start_segment.split_new(start_price_values, start_ts_values, n + 1, 1, parent=self)

            mid_price_values = prices[index1: index2]
            mid_ts_values = timestamps[index1: index2]
            self.mid_segment.split_new(mid_price_values, mid_ts_values, n + 1, 2, parent=self)

            end_price_values = prices[index2:prices_end_index]
            end_ts_values = timestamps[index2:prices_end_index]
            self.end_segment.split_new(end_price_values, end_ts_values, n + 1, 3, parent=self)
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

            self.mid_segment = None

            start_price_values = prices[0:index]
            start_ts_values = timestamps[0:index]
            self.start_segment.split_new(start_price_values, start_ts_values, n+1, 1, parent=self)

            end_price_values = prices[index:prices_end_index]
            end_ts_values = timestamps[index:prices_end_index]
            self.end_segment.split_new(end_price_values, end_ts_values, n+1, 3, parent=self)


    # recursively split prices/timestamps to create tree with start_segment, mid_segment, and end_segment
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
            self.start_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.mid_segment = None
            self.end_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0:mid_index]
            start_ts_values = timestamps[0:mid_index]
            self.start_segment.split(start_price_values, start_ts_values, n+1, 1, parent=self)

            end_price_values = prices[mid_index:-1]
            end_ts_values = timestamps[mid_index:-1]
            self.end_segment.split(end_price_values, end_ts_values, n+1, 3, parent=self)
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

            self.start_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.mid_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)
            self.end_segment = PriceSegmentNode(self.min_percent_price, self.min_segment_size)

            start_price_values = prices[0: index1]
            start_ts_values = timestamps[0: index1]
            self.start_segment.split(start_price_values, start_ts_values, n+1, 1, parent=self)

            mid_price_values = prices[index1: index2]
            mid_ts_values = timestamps[index1: index2]
            self.mid_segment.split(mid_price_values, mid_ts_values, n+1, 2, parent=self)

            end_price_values = prices[index2:-1]
            end_ts_values = timestamps[index2:-1]
            self.end_segment.split(end_price_values, end_ts_values, n+1, 3, parent=self)

        return True
