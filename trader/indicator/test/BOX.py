# New experimental indicator designed by me, calling it BOX indicator


class BOX:
    def __init__(self, window=50):
        self.window = window
        self.close_prices = []
        self.age = 0
        self.close_high = 0.0
        self.close_low = 0.0
        self.result = 0.0
        self.supports = []
        self.resistances = []

    def update(self, close):
        if len(self.close_prices) < self.window:
            self.close_prices.append(float(close))
        else:
            self.close_prices[int(self.age)] = float(close)

            if self.age == 0:
                close_high = max(self.close_prices)
                close_low = min(self.close_prices)

                if len(self.supports) == 0 or len(self.resistances) == 0:
                    self.supports.append(close_low)
                    self.resistances.append(close_high)
                elif close > max(self.resistances):
                    old_resistance = max(self.resistances)
                    self.supports.append(old_resistance)
                    self.resistances.append(close_high)
                elif close < min(self.supports):
                    old_support = min(self.supports)
                    self.resistances.append(old_support)
                    self.supports.append(close_low)

        self.age = (self.age + 1) % self.window

        if len(self.supports) == 0 or len(self.resistances) == 0:
            return 0, 0

        return self.supports[-1], self.resistances[-1]
