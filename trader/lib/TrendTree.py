from trader.lib.Crossover2 import Crossover2


class TrendTreeProcessor(object):
    def __init__(self, indicator, root_node=None):
        self.indicator = indicator
        self.direction = 0
        self.last_direction = 0
        self.cross_zero = Crossover2(window=10)

        if root_node:
            self.root_node = root_node
        else:
            self.root_node = TrendTree()

    def update(self, price, ts=0):
        value = self.indicator.update(price)
        self.cross_zero.update(value, 0)

        if self.cross_zero.crossup_detected():
            self.direction = 1
            if not self.root_node.created():
                self.root_node.create(price, self.direction, ts)
            elif self.last_direction != self.direction:
                child = TrendNode()
                child.create(price, self.direction, ts)
                self.root_node.add_child(child)
            else:
                self.root_node.update(last_price=price, last_ts=ts)

            self.last_direction = self.direction
        elif self.cross_zero.crossdown_detected():
            self.direction = -1
            if not self.root_node.created():
                self.root_node.create(price, self.direction, ts)
            elif self.last_direction != self.direction:
                child = TrendNode()
                child.create(price, self.direction, ts)
                self.root_node.add_child(child)
            else:
                self.root_node.update(last_price=price, last_ts=ts)

            self.last_direction = self.direction

class TrendNode(object):
    # create empty TrendNode
    def __init__(self):
        self.children = []
        self.parent = None
        self.direction = 0
        self.start_price = 0
        self.last_price = 0
        self.end_price = 0
        self.start_ts = 0
        self.last_ts = 0
        self.end_ts = 0
        self.created = False

    def created(self):
        return self.created

    # initialize TrendNode
    def create(self, start_price, direction=0, ts=0):
        self.direction = direction
        self.start_price = start_price
        self.start_ts = ts
        self.created = True

    def update(self, last_price=0, last_ts=0, end_price=0, end_ts=0):
        if last_price != 0:
            self.last_price = last_price
        if last_ts != 0:
            self.last_ts = last_ts
        if end_price != 0:
            self.end_price = end_price
        if end_ts != 0:
            self.end_ts = end_ts


    def add_child(self, child):
        self.children.append(child)


    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)


    def no_children(self):
        if len(self.children) == 0:
            return True
        return False

    def get_children(self):
        return self.children

    # get child's children
    def get_children_of_child(self, index):
        if len(self.children) <= index:
            return None
        return self.children[index].get_children()

    def get_child(self, index):
        if len(self.children) <= index:
            return None
        return self.children[index]

    def clear_children(self):
        self.children = []

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def contains(self, node):
        if self.end_price == 0 and self.last_price != 0:
            if node.end_price == 0 and node.last_price != 0:
                if self.start_price < node.start_price and  self.last_price > node.last_price:
                    return True
                if self.start_price > node.start_price and  self.last_price < node.last_price:
                    return True
            elif node.end_price != 0:
                if self.start_price < node.start_price and  self.last_price > node.end_price:
                    return True
                if self.start_price > node.start_price and  self.last_price < node.end_price:
                    return True

        elif self.end_price != 0:
            if node.end_price == 0 and node.last_price != 0:
                if self.start_price < node.start_price and  self.end_price > node.last_price:
                    return True
                if self.start_price > node.start_price and  self.end_price < node.last_price:
                    return True
            elif node.end_price != 0:
                if self.start_price < node.start_price and  self.end_price > node.end_price:
                    return True
                if self.start_price > node.start_price and  self.end_price < node.end_price:
                    return True

        return False


    # return True if node extends this TrendNode
    def extends(self, node, update=False):
        if self.direction != node.direction:
            return False

        if self.direction == 1:
            if self.end_price == 0 and self.last_price != 0:
                if node.end_price == 0 and node.last_price != 0:
                    if self.start_price < node.start_price < self.last_price and node.last_price > self.last_price:
                        if update:
                            self.last_price = node.last_price
                        return True
                elif node.end_price != 0:
                    if self.start_price < node.start_price < self.last_price and node.end_price > self.last_price:
                        if update:
                            self.last_price = node.end_price
                        return True
            elif self.end_price != 0:
                if node.end_price == 0 and node.last_price != 0:
                    if self.start_price < node.start_price < self.end_price and node.last_price > self.end_price:
                        if update:
                            self.end_price = node.last_price
                        return True
                elif node.end_price != 0:
                    if self.start_price < node.start_price < self.end_price and node.end_price > self.end_price:
                        if update:
                            self.end_price = node.end_price
                        return True
        elif self.direction == -1:
            if self.end_price == 0 and self.last_price != 0:
                if node.end_price == 0 and node.last_price != 0:
                    if self.start_price > node.start_price > self.last_price and node.last_price < self.last_price:
                        if update:
                            self.last_price = node.last_price
                        return True
                elif node.end_price != 0:
                    if self.start_price < node.start_price < self.last_price and node.end_price < self.last_price:
                        if update:
                            self.last_price = node.end_price
                        return True
            elif self.end_price != 0:
                if node.end_price == 0 and node.last_price != 0:
                    if self.start_price > node.start_price > self.end_price and node.last_price < self.end_price:
                        if update:
                            self.end_price = node.last_price
                        return True
                elif node.end_price != 0:
                    if self.start_price > node.start_price > self.end_price and node.end_price < self.end_price:
                        if update:
                            self.end_price = node.end_price
                        return True
        return False


    # extend self with node
    def extend(self, node):
        return self.extends(node, update=True)


class TrendTree(TrendNode):
    def __init__(self, root_node=None):
        if root_node:
            self.root_node = root_node
        else:
            super(TrendTree, self).__init__()

    def set_root(self, node):
        self.root_node = node

    def created(self):
        return self.root_node.created()

    def create(self, start_price, direction=0, ts=0):
        self.root_node.create(start_price, direction, ts)

    def update(self, last_price=0, last_ts=0, end_price=0, end_ts=0):
        self.root_node.update(last_price, last_ts, end_price, end_ts)

    def add_child(self, child):
        return self.root_node.add_child(child)

    def remove_child(self, child):
        return self.root_node.remove_child(child)

    def no_children(self):
        return self.root_node.no_children()

    def get_children(self):
        return self.root_node.get_children()

    def get_children_of_child(self, index):
        return self.root_node.get_children_of_child(index)

    def get_child(self, index):
        return self.root_node.get_child(index)

    def clear_children(self):
        self.root_node.clear_children()

    def get_parent(self):
        return self.root_node.get_parent()

    def set_parent(self, parent):
        self.root_node.set_parent(parent)

    def contains(self, node):
        return self.root_node.contains(node)

    def extends(self, node, update=False):
        return self.root_node.extends(node, update)

    def extend(self, node):
        return self.root_node.extend(node)

