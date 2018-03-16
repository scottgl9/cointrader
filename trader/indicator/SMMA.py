from trader.indicator.SMA import SMA

class SMMA:
    def __init__(self, weight=14):
        self.result = 0.0
        self.weight = weight
        self.sma = SMA(weight)

    def update(self, price):
        value = self.sma.update(price)
        if self.result == 0.0: self.result = float(price)
        else:
            self.result = (self.result * (self.weight - 1.0) + value) / self.weight
        return self.result
