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
    TYPE_MARKET = 24
    TYPE_LIMIT = 25
    TYPE_STOP_LOSS = 26
    TYPE_STOP_LOSS_LIMIT = 27
    TYPE_PROFIT_LIMIT = 28
    TYPE_TAKE_PROFIT = 29
    TYPE_LIMIT_MAKER = 30
    TYPE_NONE = 31
    SIDE_BUY = 1
    SIDE_SELL = 2
    def __init__(self, symbol, price, size, sig_id=0, buy_price=0, type=TYPE_MARKET, side=SIDE_BUY, orderid=None,
                 state='open', quote_size=0, commission=0, time_in_force=None):
        #if not orderid:
        #    self.orderid = uuid.uuid4()
        #else:
        self.orderid = orderid
        self.symbol = symbol
        self.price = float(price)
        self.buy_price = float(buy_price)
        self.size = float(size)
        self.quote_size = float(quote_size)
        self.sig_id = sig_id
        self.type = type
        self.side = side
        self.state = state
        self.commission = commission
        self.time_in_force = time_in_force

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

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return {'symbol': self.symbol,
                'id': self.orderid,
                'price': self.price,
                'size': self.size,
                'quote_size': self.quote_size,
                'sig_id': self.sig_id,
                'type': self.type,
                'commission': self.commission
                }
