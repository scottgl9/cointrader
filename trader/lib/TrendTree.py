class TrendNode(object):
    def __init__(self):
        self.children = []
        self.direction = 0
        self.start_price = 0
        self.last_price = 0
        self.end_price = 0
        self.start_ts = 0
        self.last_ts = 0
        self.end_ts = 0

    def create(self, start_price, direction=0, ts=0):
        self.direction = direction
        self.start_price = start_price
        self.start_ts = ts


    def add_child(self, child):
        self.children.append(child)


    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)


    def no_children(self):
        if len(self.children) == 0:
            return True
        return False


    def clear_children(self):
        self.children = []


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

    def create(self, start_price, direction=0, ts=0):
        self.root_node.create(start_price, direction, ts)

    def add_child(self, child):
        return self.root_node.add_child(child)

    def remove_child(self, child):
        return self.root_node.remove_child(child)

    def no_children(self):
        return self.root_node.no_children()

    def clear_children(self):
        self.root_node.clear_children()

    def contains(self, node):
        return self.root_node.contains(node)

    def extends(self, node, update=False):
        return self.root_node.extends(node, update)

    def extend(self, node):
        return self.root_node.extend(node)
