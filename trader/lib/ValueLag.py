# for a window of size N, return value N values ago


class ValueLag:
    def __init__(self, window):
        self.window = window
        self.values = []
        self.result = 0.0
        self.current_value = 0.0
        self.last_value = 0.0
        self.age = 0

    def update(self, price):
        if len(self.values) < self.window:
            tail = 0.0
            self.values.append(float(price))
            self.result = 0.0
            self.current_value = float(price)
        else:
            tail = self.values[int(self.age)]
            self.values[int(self.age)] = float(price)
            self.current_value = float(price)
            self.last_value = tail

        self.result = tail

        self.age = (self.age + 1) % self.window
        return self.result
