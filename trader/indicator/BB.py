# Bollinger Bands (BB)

from trader.indicator.SMA import SMA
from trader.indicator.STDDEV import STDDEV
from trader.lib.ValueLag import ValueLag


class BollingerBands:
    def __init__(self, weight=20, dev_count=2.0, smoother=None):
        self.result = 0.0
        self.last_result = 0.0
        self.weight = float(weight)
        self.dev_count = dev_count
        if not smoother:
            self.smoother = SMA(weight)
        else:
            self.smoother = smoother
        self.stddev = STDDEV(weight)
        self.mid_band = 0.0
        self.low_band = 0.0
        self.high_band = 0.0

    def ready(self):
        return self.stddev.ready()

    def update(self, price, ts=0):
        self.mid_band = self.smoother.update(price)
        value = self.stddev.update(price)
        if value != 0.0:
            self.low_band = self.mid_band - (self.dev_count * value)
            self.high_band = self.mid_band + (self.dev_count * value)
