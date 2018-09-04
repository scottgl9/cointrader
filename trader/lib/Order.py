import uuid
from trader.lib.Message import Message


class OrderList(object):
    def __init__(self):
        self.orders = []

    def prices(self):
        result = []
        for order in self.orders:
            result.append(order.price)
        return result

    def sizes(self):
        result = []
        for order in self.orders:
            result.append(order.size)
        return result

    def price_in_range(self, price):
        prices = self.prices()
        if min(prices) <= price < max(prices):
            return True
        return False

    def __contains__(self, check_price):
        for price in self.prices():
            if price == check_price:
                return True
        return False

    def __gt__(self, other):
        return other.price > max(self.prices())

    def __lt__(self, other):
        return other.price < min(self.prices())

    def __repr__(self):
        return self.prices

    def append(self, order):
        self.orders.append(order)

    def remove(self, order):
        self.orders.remove(order)


class Order(object):
    def __init__(self, symbol, price, size, type=Message.MSG_MARKET_BUY, orderid=None, state='open'):
        if not orderid:
            self.orderid = uuid.uuid4()
        else:
            self.orderid = id
        self.symbol = symbol
        self.price = float(price)
        self.size = float(size)
        self.type = type
        self.state = state

    def __lt__(self, other):
        return self.price < other.price

    # return comparison
    def __eq__(self, other):
        return self.price == other.price

    # return comparison
    def __ne__(self, other):
        return self.price != other.price

    # return comparison
    def __gt__(self, other):
        return self.price > other.price

    def __len__(self):
        return self.size

    def __repr__(self):
        return {'id': self.orderid, 'price': self.price, 'size': self.size, 'type': self.type}
