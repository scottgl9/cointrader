class SMA:
    def __init__(self, window):
        self.window = window
        self.prices = []
        self.result = 0.0
        self.age = 0
        self.sum = 0.0

    def update(self, price):
        tail = 0.0
        if len(self.prices) < self.window:
            tail = 0.0
            self.prices.append(float(price))
        else:
            tail = self.prices[int(self.age)]
            self.prices[int(self.age)] = float(price)

        self.sum += float(price) - tail
        if len(self.prices) != 0:
            self.result = self.sum / float(len(self.prices))
        self.age = (self.age + 1) % self.window
        return self.result
