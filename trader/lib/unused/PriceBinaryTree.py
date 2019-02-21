class PriceBinaryTree(object):
    def __init__(self, filter=None):
        self.root = None
        self.filter = filter
        self.last_result = 0
        self.result = 0
        self.last_ts = 0
        self.ts = 0

    def update(self, price, ts=0):
        if not self.filter:
            return

        result = self.filter.update(float(price))

        if result == 0:
            return

        self.last_result = self.result
        self.result = result
        self.last_ts = self.ts
        self.ts = ts

        if self.last_result == 0 or self.result == 0:
            return

        if self.no_root():
            self.create_root(self.last_result, self.result, self.last_ts, self.ts)


    def no_root(self):
        return self.root == None

    def create_root(self, price_start, price_end, ts_start=0, ts_end=0):
        self.root = PriceBinaryNode(price_start, price_end, ts_start, ts_end)

    def get_root(self):
        return self.root

    def set_root(self, node):
        self.root=node

    def get_left(self):
        if self.root:
            return self.root.left
        return None

    def get_right(self):
        if self.root:
            return self.root.right
        return None

    def set_left(self, node):
        if self.root:
            self.root.left = node

    def set_right(self, node):
        if self.root:
            self.root.right = node


class PriceBinaryNode(object):
    def __init__(self, price_start, price_end, ts_start=0, ts_end=0):
        self.left = None
        self.right = None
        self.price_start = price_start
        self.price_end = price_end
        self.ts_start = ts_start
        self.ts_end = ts_end

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def set_left(self, node):
        self.left = node

    def set_right(self, node):
        self.right = node
