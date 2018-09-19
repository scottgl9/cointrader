# filter prices which are already in prices window
from trader.indicator.EMA import EMA
from trader.indicator.ZLEMA import ZLEMA
from trader.indicator.STDDEV import STDDEV

class PriceFilter(object):
    def __init__(self, window=5):
        self.stddev = STDDEV(window=window)
        self.ema = ZLEMA(window, scale=60)
        self.window = window
        self.last_price = 0
        self.result = 0

    def update(self, price):
        self.stddev.update(float(price))
        self.ema.update(float(price))

        if abs(price - self.ema.result) > 0.5 * self.stddev.result:
            self.result = self.ema.result
        else:
            self.result = float(price)

        self.last_price = self.result
        return self.result
