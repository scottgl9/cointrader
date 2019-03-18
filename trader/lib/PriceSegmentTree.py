# Class derrived from LargestPriceChange class (LPC) that I wrote which takes prices/timestamps and recursively
# builds a tree with three child nodes: seg_start, seg_mid, and end_segment
from trader.lib.PriceSegmentNode import PriceSegmentNode


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

        if node.seg_start:
            self._walk_leaf_nodes(node.seg_start)

        if node.seg_mid:
            self._walk_leaf_nodes(node.seg_mid)

        if node.seg_end:
            self._walk_leaf_nodes(node.seg_end)

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

        if node.seg_start:
            self._walk_node_depth_dict(node.seg_start, n+1)

        if node.seg_mid:
            self._walk_node_depth_dict(node.seg_mid, n+1)

        if node.seg_end:
            self._walk_node_depth_dict(node.seg_end, n+1)

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

        if node1.seg_start and node2.seg_start:
            tnext = t
            tnext.append(1)
            self.compare(node1.seg_start, node2.seg_start, n + 1, tnext)

        if node1.seg_mid and node2.seg_mid:
            tnext = t
            tnext.append(2)
            self.compare(node1.seg_mid, node2.seg_mid, n + 1, tnext)

        if node1.seg_end and node2.seg_end:
            tnext = t
            tnext.append(3)
            self.compare(node1.seg_end, node2.seg_end, n + 1, tnext)

    def get_compare_results(self):
        return {'n': self._compare_n, 't': self._compare_t, 'node1': self._compare_node1, 'node2': self._compare_node2}
