# restrict maximum price fluctuation based on minimum tick increment size
from trader.lib.CircularArray import CircularArray

class TickFilter(object):
    def __init__(self, tick_size=0.0, window=4):
        self.tick_size = float(tick_size)
        self.window = window
        self.prices = CircularArray(window=(self.window+1), reverse=True)
        self.result = 0
        self.last_result = 0

    def update(self, price):
        if self.tick_size == 0:
            return float(price)

        self.prices.add(float(price))

        if len(self.prices) < self.prices.window:
            return self.result

        self.last_result = self.result
        self.result = float(price)

        for i in range(1, self.window):
            if abs(self.prices[0] - self.prices[i]) > self.tick_size:
                self.result = 0 #self.last_result
                break

        return self.result
