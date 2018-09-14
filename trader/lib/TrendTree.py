class TrendNode(object):
    def __init__(self, start_price, direction=0, ts=0):
        self.children = []
        self.direction = direction
        self.start_price = start_price
        self.last_price = 0
        self.end_price = 0
        self.start_ts = ts
        self.last_ts = 0
        self.end_ts = 0


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


class TrendTree(object):
    def __init__(self, root_node=None):
        self.root_node = root_node


    def set_root(self, node):
        self.root_node = node

