# Elder's Force Index (EFI)
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.lib.ValueLag import ValueLag
from trader.indicator.EMA import EMA


class EFI(IndicatorBase):
    def __init__(self, window=13, scale=1):
        IndicatorBase.__init__(self, use_close=True, use_volume=True)
        self.window = window
        self.scale = scale
        self.lag = ValueLag(window=self.window)
        self.ema = EMA(window, scale=scale)
        self.result = 0

    def update(self, price, volume, ts=0):
        self.lag.update(float(price))

        if self.lag.result == 0:
            return self.result

        fi1 = (float(price) - self.lag.result) * float(volume)
        self.ema.update(fi1)

        if self.ema.count < self.ema.weight:
            return self.result

        self.result = self.ema.result

        return self.result
