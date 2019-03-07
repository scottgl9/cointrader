# Class derrived from LargestPriceChange class (LPC) that I wrote.


class PriceSegmentTree(object):
    def __init__(self, prices=None, timestamps=None, use_dict=False):
        self.use_dict = use_dict
        self.prices = None
        self.timestamps = None
        self.root = None
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
        self.root = PriceSegmentNode(self.prices, self.timestamps)

    def divide_price_segments(self):
        self.root.split()

    # def price_segments(self, node=None, type=0, score=0.0, n=0):
    #     if not node:
    #         node = self.root
    #
    #     entry = None
    #     rscore = 0
    #
    #     if n:
    #         rscore = self.round_score(score/n)
    #         if self.use_dict:
    #             entry = {'percent': float(node.percent),
    #                      'start_ts': int(node.start_ts),
    #                      'end_ts': int(node.end_ts),
    #                      'diff_ts': int(node.diff_ts),
    #                      'start_price': float(node.start_price),
    #                      'end_price': float(node.end_price)}
    #         else:
    #             entry = LPCSegment(node.percent, node.start_ts, node.end_ts, node.start_price,
    #                                node.end_price, type, rscore, n)
    #
    #     if entry:
    #         self._price_segment_percents.append(entry)
    #         if rscore == 1:
    #             self._price_segment_score1.append(entry)
    #         elif rscore == 2:
    #             self._price_segment_score2.append(entry)
    #         elif rscore == 3:
    #             self._price_segment_score3.append(entry)
    #
    #     if not node.child:
    #         return
    #
    #     if node.child.start_segment:
    #         t = LPCSegment.TYPE_SEGMENT_START
    #         self.price_segments(node.child.start_segment, type=t, score=float(score + t), n=n+1)
    #     if node.child.mid_segment:
    #         t = LPCSegment.TYPE_SEGMENT_MID
    #         self.price_segments(node.child.mid_segment, type=t, score=float(score + t), n=n+1)
    #     if node.child.end_segment:
    #         t = LPCSegment.TYPE_SEGMENT_END
    #         self.price_segments(node.child.end_segment, type=t, score=float(score + t), n=n+1)
    #
    # def round_score(self, score):
    #     score = float(score)
    #     if score < 1.5:
    #         result = 1
    #     elif score < 2.5:
    #         result = 2
    #     else:
    #         result = 3
    #     return result


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
        self.start_segment = None           # start PriceSegment
        self.mid_segment = None             # mid PriceSegment
        self.end_segment = None             # end PriceSegment
        # percent change of price segment
        self.percent = round(100.0 * (self.end_price - self.start_price) / self.start_price, 2)

    def split(self, prices, timestamps):
        self.start_price = prices[0]
        self.end_price = prices[-1]
        self.start_ts = timestamps[0]
        self.end_ts = timestamps[-1]

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
        if 100.0*(self.max_price - self.min_price) / self.min_price <= self.min_percent_price:
            return False

        # Too small to split into three segments, so return
        if len(prices) <= (3 * self.min_segment_size):
            return False

        half_split = False

        # if mid segment size is less than min_segment_size, set half_split mode
        if abs(self.max_price_index - self.min_price_index) < self.min_segment_size:
            half_split = True

        # if start or end segment size is less than min_segment_size, set half_split mode
        if self.min_price_index < self.max_price_index:
            if self.min_price_index < self.min_segment_size:
                half_split = True
            if (len(prices) - self.max_price_index) < self.min_segment_size:
                half_split = True
        elif self.min_price_index > self.max_price_index:
            if self.max_price_index < self.min_segment_size:
                half_split = True
            if (len(prices) - self.min_price_index) < self.min_segment_size:
                half_split = True
        else:
            return False

        if half_split:
            mid_index = int(len(prices) / 2)
            start_price_values = prices[0:mid_index]
            start_ts_values = timestamps[0:mid_index]
            end_price_values = prices[mid_index:-1]
            end_ts_values = timestamps[mid_index:-1]
            self.mid_segment = None
            self.start_segment = PriceSegmentNode()
            self.end_segment = PriceSegmentNode()

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

            self.start_segment = PriceSegmentNode()
            self.mid_segment = PriceSegmentNode()
            self.end_segment = PriceSegmentNode()

            self.start_segment.split(start_price_values, start_ts_values)
            self.mid_segment.split(mid_price_values, mid_ts_values)
            self.end_segment.split(end_price_values, end_ts_values)

        return True
