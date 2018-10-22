from trader.indicator.SMA import SMA

class SMMA:
    def __init__(self, weight=14, scale=1):
        self.result = 0.0
        self.weight = weight
        self.scale = scale
        self.sma = SMA(weight)

    def update(self, price):
        value = self.sma.update(price)
        if self.result == 0.0: self.result = float(price)
        else:
            if self.scale == 1:
                self.result = (self.result * (self.weight - 1.0) + value) / self.weight
            else:
                weight = float(self.weight * self.scale)
                self.result = (self.result * (weight - 1.0) + value) / weight

        return self.result
