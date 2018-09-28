# Bollinger BandWidth
from trader.indicator.BB import BollingerBands

class BollingerBandwidth(object):
    def __init__(self, weight=20, dev_count=2.0):
        self.bb = BollingerBands(weight=weight, dev_count=dev_count)
        self.result = 0

    def update(self, price):
        self.bb.update(price)

        if self.bb.mid_band == 0 or self.bb.low_band == 0 or self.bb.high_band == 0:
            return self.result

        self.result = 100 * (self.bb.high_band - self.bb.low_band) / self.bb.mid_band

        return self.result