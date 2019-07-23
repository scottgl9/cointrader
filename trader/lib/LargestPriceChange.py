# Class to analyze a data set of prices / timestamps. Result is a sorted list of percent price changes
# along with the start_ts, end_ts for each segment
from trader.lib.PriceSegmentTree import PriceSegmentTree, PriceSegmentNode


class LargestPriceChange(object):
    def __init__(self, prices=None, timestamps=None, use_dict=False):
        self.use_dict = use_dict
        self.prices = None
        self.timestamps = None
        self.tree = None
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
        self.tree = PriceSegmentTree(self.prices, self.timestamps)
        self._price_segment_percents = []

    def divide_price_segments(self):
        self.tree.split()

    def get_price_segments(self, leaves_only=False):
        self._price_segment_percents = []
        self.price_segments(node=self.tree.root, leaves_only=leaves_only)
        return self._price_segment_percents

    def get_price_segments_percent_sorted(self, leaves_only=False, reverse=False):
        self.get_price_segments(leaves_only)
        # sort by percent
        if self.use_dict:
            self._price_segment_percents.sort(key=lambda x: x['percent'], reverse=reverse)
        else:
            self._price_segment_percents.sort(key=lambda x: x.percent, reverse=reverse)

        return self._price_segment_percents

    def get_price_segments_score_sorted(self, leaves_only=False, reverse=False):
        self.get_price_segments(leaves_only)
        # sort by percent
        if self.use_dict:
            self._price_segment_percents.sort(key=lambda x: x['score'], reverse=reverse)
        else:
            self._price_segment_percents.sort(key=lambda x: x.score, reverse=reverse)

        return self._price_segment_percents

    # return largest negative price change, and largest positive price change
    def get_largest_price_segment_percents(self, leaves_only=False):
        price_segment_percents = self.get_price_segments_percent_sorted(leaves_only)
        seg_down = None
        seg_up = None

        # indicate only one price segment found
        if len(price_segment_percents) == 1:
            if price_segment_percents[0].percent < 0:
                seg_down = price_segment_percents[0]
            elif price_segment_percents[0].percent > 0:
                seg_up = price_segment_percents[0]
        else:
            seg_down = price_segment_percents[0]
            seg_up = price_segment_percents[-1]

        return [seg_down, seg_up]

    def price_segments(self, node=None, type=0, score=0.0, n=0, leaves_only=False):
        entry = None
        rscore = 0

        if n and (not leaves_only or (leaves_only and node.leaf)):
            rscore = self.round_score(score/n)
            node.update_percent()
            if self.use_dict:
                entry = {'percent': float(node.percent),
                         'start_ts': int(node.start_ts),
                         'end_ts': int(node.end_ts),
                         'diff_ts': int(node.diff_ts),
                         'start_price': float(node.start_price),
                         'end_price': float(node.end_price)}
            else:
                entry = LPCSegment(node.percent, node.start_ts, node.end_ts, node.start_price,
                                   node.end_price, type, rscore, n, node.leaf)

        if entry:
            self._price_segment_percents.append(entry)

        if node.seg_start:
            t = LPCSegment.TYPE_SEGMENT_START
            self.price_segments(node.seg_start, type=t, score=float(score + t), n=n+1, leaves_only=leaves_only)
        if node.seg_mid:
            t = LPCSegment.TYPE_SEGMENT_MID
            self.price_segments(node.seg_mid, type=t, score=float(score + t), n=n+1, leaves_only=leaves_only)
        if node.seg_end:
            t = LPCSegment.TYPE_SEGMENT_END
            self.price_segments(node.seg_end, type=t, score=float(score + t), n=n+1, leaves_only=leaves_only)

    def round_score(self, score):
        score = float(score)
        if score < 1.5:
            result = 1
        elif score < 2.5:
            result = 2
        else:
            result = 3
        return result


class LPCSegment(object):
    TYPE_SEGMENT_NONE = 0
    TYPE_SEGMENT_START = 1
    TYPE_SEGMENT_MID = 2
    TYPE_SEGMENT_END = 3

    def __init__(self, percent=0, start_ts=0, end_ts=0, start_price=0, end_price=0, type=0, score=0.0, depth=0,
                 leaf=False):
        self.start_ts = int(start_ts)
        self.end_ts = int(end_ts)
        self.percent = float(percent)
        self.diff_ts = end_ts - start_ts
        self.start_price = float(start_price)
        self.end_price = float(end_price)
        self.type = type
        self.score = score
        self.depth = depth
        self.leaf = leaf

    def __getitem__(self, item):
        if item == "percent":
            return float(self.percent)
        elif item == 'start_ts':
            return int(self.start_ts)
        elif item == 'end_ts':
            return int(self.end_ts)
        elif item == 'diff_ts':
            return int(self.diff_ts)
        elif item == 'start_price':
            return float(self.start_price)
        elif item == 'end_price':
            return float(self.end_price)
        elif item == 'type':
            return int(self.type)
        elif item == 'depth':
            return int(self.depth)
        elif item == 'leaf':
            return self.leaf

    def __lt__(self, other):
        if self.percent < other.percent:
            return True
        return False

    def __repr__(self):
        return str(self.__dict__())

    def __dict__(self):
        return {'start_ts': self.start_ts, 'end_ts': self.end_ts, 'diff_ts': self.diff_ts,
                'percent': self.percent, 'type': self.type, 'score': self.score, 'depth': self.depth,
                'start_price': self.start_price, 'end_price': self.end_price, 'leaf': self.leaf}
