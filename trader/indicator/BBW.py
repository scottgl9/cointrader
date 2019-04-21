# Bollinger BandWidth
from .IndicatorBase import IndicatorBase
from trader.indicator.BB import BollingerBands

class BollingerBandwidth(IndicatorBase):
    def __init__(self, weight=20, dev_count=2.0):
        IndicatorBase.__init__(self, use_close=True)
        self.bb = BollingerBands(weight=weight, dev_count=dev_count)
        self.result = 0

    def update(self, price, ts=0):
        self.bb.update(price)

        if self.bb.mid_band == 0 or self.bb.low_band == 0 or self.bb.high_band == 0:
            return self.result

        self.result = 100 * (self.bb.high_band - self.bb.low_band) / self.bb.mid_band

        return self.result
