# filter prices which are already in prices window


class PriceFilter(object):
    def __init__(self, window=20, range_filter=False, minmax_filter=False):
        self.prices = []
        self.window = window
        self.age = 0
        self.result = 0
        self.range_filter = range_filter
        self.minmax_filter = minmax_filter
        self.min_price = 0
        self.max_price = 0
        self.last_price = 0
        self.prev_last_price = 0
        self.prev_prev_last_price = 0

    def update(self, price):
        # prices outside of range of prices have to retest price to be entered into prices
        if self.minmax_filter and len(self.prices) > 0:
            if self.min_price == 0:
                if price < min(self.prices):
                    self.min_price = price
                    self.result = 0
                    return self.result
            if self.max_price == 0:
                if price > max(self.prices):
                    self.max_price = price
                    self.result = 0
                    return self.result

        if self.range_filter and len(self.prices) > 0:
            if min(self.prices) <= float(price) <= max(self.prices):
                return self.result

        if float(price) in self.prices:
            return self.result

        if len(self.prices) < self.window:
            self.prices.append(float(price))
        else:
            self.prices[int(self.age)] = float(price)

        if (self.prev_last_price == 0 or
            self.last_price == 0 or
            float(price) > self.last_price > self.prev_last_price or
            float(price) < self.last_price < self.prev_last_price):
            self.result = self.last_price
            if self.last_price != self.prev_last_price:
                self.prev_last_price = self.last_price
            self.last_price = float(price)
        else:
            self.result = self.prev_last_price
            self.last_price = float(price)

        self.age = (self.age + 1) % self.window

        return self.result
