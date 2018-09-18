from trader.lib.Crossover2 import Crossover2


# create root node, and process price/ts updates
class TrendTreeProcessor(object):
    def __init__(self, indicator, root_node=None, logger=None):
        self.indicator = indicator
        self.direction = 0
        self.last_direction = 0
        self.cross_zero = Crossover2(window=10)
        self.time_node_end = 1000 * 3600 # 1 hour
        self.logger = logger

        if root_node:
            self.root_node = root_node
        else:
            self.root_node = TrendTree()

    def check_node_ended(self, node, ts):
        if node.last_ts == 0:
            return False
        if node.is_ended() or (ts - node.last_ts) > self.time_node_end:
            return True
        return False

    def print_tree(self, node=None):
        if not node:
            node = self.root_node

        if not node.is_created():
            return

        self.logger.info("NODE: {} {} {} {} {}".format(node.start_price,
                                                       node.start_ts,
                                                       node.last_price,
                                                       node.last_ts,
                                                       node.direction))

        if node.no_children():
            return
        for child in node.get_children():
            self.print_tree(child)

    def update(self, price, ts=0):
        crossed = False
        value = self.indicator.update(price)
        self.cross_zero.update(value, 0)

        # if trending upward
        if self.cross_zero.crossup_detected():
            self.direction = 1
            crossed = True
        # if trending downward
        elif self.cross_zero.crossdown_detected():
            self.direction = -1
            crossed = True

        if crossed:
            # if root node hasn't been created, create it
            if not self.root_node.is_created():
                self.root_node.create(price, self.direction, ts)
            # if trend direction is opposite of root node
            elif self.direction != self.root_node.direction:
                # if root node has no children, create child
                if self.root_node.no_children():
                    child = TrendNode()
                    child.create(price, self.direction, ts)
                    self.root_node.add_child(child)
                else:
                    last_child = self.root_node.get_last_child()
                    if self.check_node_ended(last_child, ts):
                        child = TrendNode()
                        child.create(price, self.direction, ts)
                        self.root_node.add_child(child)
                        # mark last child as done
                        last_child.end()
                    else:
                        last_child.update(last_price=price, last_ts=ts)
                        # last_child downward trend supercedes root, so replace root with child
                        if self.root_node.direction == 1 and price < self.root_node.start_price:
                            old_root_node = self.root_node
                            self.root_node = last_child
                            old_root_node.remove_child(last_child)
                            self.root_node.add_child(old_root_node)
                        # last_child upward trend supercedes root, so replace root with child
                        elif self.root_node.direction == -1 and price > self.root_node.start_price:
                            old_root_node = self.root_node
                            self.root_node = last_child
                            old_root_node.remove_child(last_child)
                            self.root_node.add_child(old_root_node)
            else:
                # trend direction hasn't changed, so update root node
                self.root_node.update(last_price=price, last_ts=ts)

            #self.last_direction = self.direction


class TrendNode(object):
    # create empty TrendNode
    def __init__(self):
        self.children = []
        self.parent = None
        self.direction = 0
        self.start_price = 0
        self.start_ts = 0
        self.last_price = 0
        self.last_ts = 0
        self.created = False
        self.ended = False

    def is_created(self):
        return self.created

    def is_ended(self):
        return self.ended

    # mark that we are done updating this node
    def end(self):
        self.ended = True

    # initialize TrendNode
    def create(self, start_price, direction=0, ts=0):
        self.direction = direction
        self.start_price = start_price
        self.start_ts = ts
        self.created = True

    def update(self, last_price=0, last_ts=0):
        if not self.created:
            return

        if last_price != 0:
            self.last_price = last_price
        if last_ts != 0:
            self.last_ts = last_ts

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

    def get_last_child(self):
        if self.no_children():
            return None
        return self.children[-1]

    def clear_children(self):
        self.children = []

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    # if node range is contained within this node range, return True
    def contains(self, node):
        if self.last_price != 0 and node.last_price != 0:
            if self.start_price < node.start_price and  self.last_price > node.last_price:
                return True
            if self.start_price > node.start_price and  self.last_price < node.last_price:
                return True

        return False

    # return True if node extends this TrendNode, if update is True then also extend this node from node
    def extends(self, node, update=False):
        if self.direction != node.direction:
            return False

        if self.direction == 1:
            if self.last_price != 0 and node.last_price != 0:
                # if start of node in range of this node, and last of node is outside range of last of this node
                if self.start_price < node.start_price < self.last_price and node.last_price > self.last_price:
                    if update:
                        self.last_price = node.last_price
                        self.last_ts = node.last_ts
                    return True
        elif self.direction == -1:
            if self.last_price != 0 and node.last_price != 0:
                # if start of node in range of this node, and last of node is outside range of last of this node
                if self.start_price > node.start_price > self.last_price and node.last_price < self.last_price:
                    if update:
                        self.last_price = node.last_price
                        self.last_ts = node.last_ts
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
            self.root_node = super(TrendTree, self).__init__()

    def set_root(self, node):
        self.root_node = node

    def is_created(self):
        return self.root_node.is_created()

    def is_ended(self):
        return self.root_node.is_ended()

    # mark that we are done updating this node
    def end(self):
        self.root_node.end()

    def create(self, start_price, direction=0, ts=0):
        self.root_node.create(start_price, direction, ts)

    def update(self, last_price=0, last_ts=0):
        self.root_node.update(last_price, last_ts)

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

    def get_last_child(self):
        return self.root_node.get_last_child()

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
