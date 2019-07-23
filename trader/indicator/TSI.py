from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.EMA import EMA


class TSI(IndicatorBase):
    def __init__(self, weight1=25.0, weight2=13.0):
        IndicatorBase.__init__(self, use_close=True)
        self.result = 0.0
        self.weight1 = weight1
        self.weight2 = weight2
        self.ema_pc1 = EMA(self.weight1)
        self.ema_pc2 = EMA(self.weight2)
        self.ema_apc1 = EMA(self.weight1)
        self.ema_apc2 = EMA(self.weight2)
        self.last_price = 0.0
        self.count = 0

    def update(self, price, ts=0):
        if float(self.count) < self.weight1:
            self.count += 1
        if self.last_price == 0.0:
            self.last_price = price
            return 0.0
        pc = price - self.last_price
        apc = abs(price - self.last_price)
        dspc = self.ema_pc2.update(self.ema_pc1.update(pc))
        dsapc = self.ema_apc2.update(self.ema_apc1.update(apc))
        self.result = 0.0
        if dsapc != 0.0:
            self.result = 100.0 * (dspc / dsapc)
        self.last_price = price
        if float(self.count) < self.weight1:
            return 0.0
        else:
            return self.result
