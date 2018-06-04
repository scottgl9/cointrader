# If only close prices are available in realtime, create fake kline data from the close prices
from trader.lib.CircularArray import CircularArray


class FakeKline(object):
    def __init__(self, window=5):
        self.window = window
        self.values = CircularArray(window=window)
        self.last_close = 0
        self.open = 0
        self.low = 0
        self.high = 0

    # kline return format: [open, close, low, high, volume]
    def update(self, close, volume=0):
        if self.last_close == 0:
            self.last_close = close
            self.open = close
            self.low = close
            self.high = close
            return close, close, close, close, volume

        if close == self.last_close:
            return self.open, close, self.low, self.high, volume

        self.open = self.last_close
        self.values.add(float(close))
        self.low = self.values.min()
        self.high = self.values.max()
        self.last_close = float(close)

        return self.open, close, self.low, self.high, volume
