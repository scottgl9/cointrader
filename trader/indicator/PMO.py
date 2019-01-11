# DecisionPoint Price Momentum Oscillator (PMO)
from trader.indicator.EMA import EMA
from trader.lib.ValueLag import ValueLag


class PMO:
    def __init__(self, p1=35, p2=20, p3=10, scale=1.0):
        self.result = 0.0
        self.last_result = 0.0
        self.last_price = 0.0
        self.rocma = 0.0
        self.pmo = 0.0
        self.pmo_signal = 0.0
        self.p1 = float(p1)
        self.p2 = float(p2)
        self.p3 = float(p3)
        self.ema1 = EMA(p1, scale=scale, custom=True)
        self.ema2 = EMA(p2, scale=scale, custom=True)
        self.ema3 = EMA(p3, scale=scale, custom=False)
        self.scale = scale
        self.count = 0

    def update(self, price, ts=0):
        if self.last_price == 0:
            self.last_price = price
            return self.result

        roc = 100.0 * (price - self.last_price) / self.last_price
        self.rocma = self.ema1.update(roc)
        self.pmo = self.ema2.update(self.rocma)
        self.pmo_signal = self.ema3.update(self.pmo)

        return self.result
