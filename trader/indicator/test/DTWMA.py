# Indicator I designed called Delta Time/Timestamp Weighted Moving Average
from trader.lib.CircularArray import CircularArray

class DTWMA(object):
    def __init__(self, window):
        self.window = window
        self.timestamps = CircularArray(window=window)
        self.ts_deltas = CircularArray(window=window)
        self.prices = CircularArray(window=window)
        self.lag = (self.window - 1) / 2
        self.result = 0

    def update(self, price, ts):
        self.prices.add(price)

        if not self.timestamps.empty():
            self.ts_deltas.add((ts - self.timestamps.last())/1000.0)

        self.timestamps.add(ts)

        if not self.ts_deltas.full():
            self.result = price
            return self.result

        deltas = self.ts_deltas.values_ordered()
        prices = self.prices.values_ordered()

        total = 0
        avg_price = 0

        for i in range(0, self.window - 1):
            avg_price += deltas[i] * prices[i]
            total += deltas[i]

        self.result = avg_price / total

        return self.result
