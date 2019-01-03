# for a window of size N, return value N values ago


class ValueLag:
    def __init__(self, window):
        self.window = window
        self.values = []
        self.result = 0.0
        self.age = 0

    def full(self):
        return len(self.values) == self.window

    def ready(self):
        return len(self.values) == self.window

    def update(self, price):
        if len(self.values) < self.window:
            self.values.append(float(price))
            return self.result

        tail = self.values[int(self.age)]
        self.values[int(self.age)] = float(price)

        self.result = tail

        self.age = (self.age + 1) % self.window
        return self.result
