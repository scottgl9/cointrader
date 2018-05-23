# keeps track of multiple market buy orders, and order completed when sold at X%
def percent_p2_gt_p1(p1, p2, percent):
    if p1 == 0: return False
    if p2 <= p1: return False
    result = 100.0 * (float(p2) - float(p1)) / float(p1)
    if result <= percent:
        return False
    return True


class TradeStack(object):
    def __init__(self, percent, size=1):
        self.size = size
        self.percent = percent
        self.buy_order_list = []

    def can_buy(self):
        if len(self.buy_order_list) >= self.size:
            return False

        return True

    def can_sell(self, price):
        pass

    def add_buy(self, buy_price, buy_qty):
        if not self.can_buy():
            return False

        self.buy_order_list.append((buy_price, buy_qty))
        return True

    def sell_qty(self, price):
        if not self.can_sell(price):
            return 0.0

        qty = 0.0
        for (buy_price, buy_qty) in self.buy_order_list:
            if percent_p2_gt_p1(buy_price, price, self.percent):
                qty += buy_qty

        return qty

    def sell_completed(self, price):
        for (buy_price, buy_qty) in self.buy_order_list:
            if percent_p2_gt_p1(buy_price, price, self.percent):
                self.buy_order_list.remove((buy_price, buy_qty))
