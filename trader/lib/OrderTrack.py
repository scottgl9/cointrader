# track orders, set maximum number of orders, and set order type
from trader.lib.Order import Order


def percent_p2_gt_p1(p1, p2, percent):
    if p1 == 0: return False
    if p2 <= p1: return False
    result = 100.0 * (float(p2) - float(p1)) / float(p1)
    if result <= percent:
        return False
    return True


class OrderTrack(object):
    MARKET_ORDER = 1
    LIMIT_ORDER = 2
    STOP_ORDER = 3

    def __init__(self, order_type, max_order_count=1, percent=1.0):
        self.orders = []
        self.max_order_count = max_order_count
        self.order_type = order_type
        self.percent = percent

    def can_buy(self):
        if len(self.orders) == self.max_order_count:
            return False
        return True

    def buy(self, price, size):
        if not self.can_buy():
            return False

        order = Order(price=price, size=size)
        self.orders.append(order)

        return True

    def can_sell(self):
        if len(self.orders) > 0:
            return True
        return False

    def sell(self, price):
        size = 0.0
        remove_orders = []
        for order in self.orders:
            if order.price >= price:
                continue
            if percent_p2_gt_p1(order.price, price, self.percent):
                remove_orders.append(order)
                size += order.size

        for order in remove_orders:
            if order in self.orders:
                self.orders.remove(order)

        return size
