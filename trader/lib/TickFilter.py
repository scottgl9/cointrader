from trader.lib.CircularArray import CircularArray

class TickFilter(object):
    def __init__(self, tick_size=0.0, window=26):
        self.tick_size = tick_size
        self.window = window
        self.prices = CircularArray(window=self.window, reverse=True)
        self.result = 0

    def update(self, price):
        self.prices.add(float(price))

        if len(self.prices) < self.prices.window:
            return self.result

        if abs(self.prices[0] - self.prices[1]) > (self.tick_size * self.window):
            self.result = 0
        else:
            self.result = float(price)

        return self.result

