from trader.indicator.SMMA import SMMA


class RSI:
    def __init__(self, weight=14):
        self.lastClose = None
        self.weight = weight
        self.avgU = SMMA(self.weight)
        self.avgD = SMMA(self.weight)
        self.u = 0.0
        self.d = 0.0
        self.rs = 0.0
        self.result = 0.0
        self.age = 0

    def update(self, priceclose):
        currentclose = float(priceclose)

        if not self.lastClose:
            # Set initial price to prevent invalid change calculation
            self.lastClose = currentclose

            # Do not calculate RSI for this reason - there's no change!
            self.age += 1
            return

        if currentclose > self.lastClose:
            self.u = currentclose - self.lastClose
            self.d = 0.0

        else:
            self.u = 0.0
            self.d = self.lastClose - currentclose

        self.avgU.update(self.u)
        self.avgD.update(self.d)

        if self.avgD.result == 0.0 and self.avgU.result != 0.0:
            self.result = 100.0
        elif self.avgD.result == 0.0:
            self.result = 0.0
        else:
            self.rs = self.avgU.result / self.avgD.result
            self.result = 100.0 - (100.0 / (1.0 + self.rs))

        self.lastClose = currentclose
        self.age += 1
        return self.result
