# Indicator I designed called Delta Time/Timestamp Weighted Moving Average
from trader.lib.struct.CircularArray import CircularArray
from trader.lib.struct.IndicatorBase import IndicatorBase


class DTWMA(IndicatorBase):
    def __init__(self, window=10, smoother=None):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.window = window
        self.timestamps = CircularArray(window=window)
        self.ts_deltas = CircularArray(window=window)
        self.prices = CircularArray(window=window)
        self.smoother = smoother
        self.lag = (self.window - 1) / 2
        self.result = 0

    def ready(self):
        return self.ts_deltas.full()

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

        total = 1
        avg_price = prices[0]

        for i in range(1, self.window - 1):
            avg_price += deltas[i] * prices[i]
            total += deltas[i]

        if self.smoother:
            self.result = self.smoother.update(avg_price / total)
        else:
            self.result = avg_price / total

        return self.result
