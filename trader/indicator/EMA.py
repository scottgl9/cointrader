from trader.indicator.SMA import SMA


class EMA:
    def __init__(self, weight=26, scale=1.0):
        self.result = 0.0
        self.last_result = 0.0
        self.prev_last_result = 0.0
        self.weight = float(weight)
        self.scale = scale
        self.sma = SMA(weight)

    def update(self, price):
        if self.result == 0.0:
            self.prev_last_result = self.last_result
            self.last_result = self.result
            self.result = self.sma.update(price)
            return self.result
        else:
            k = 2.0 / (self.weight * self.scale + 1.0)
            y = self.result
            self.prev_last_result = self.last_result
            self.last_result = self.result
            self.result = self.sma.update(price) * k + y * (1.0 - k)
            return self.result
