# Tick imbalance bars (TIB)

class TIB(object):
    def __init__(self, window):
        self.window = window
        self.prev_close = 0
        self.b = 0
        self.b_values = []
        self.b_sum = 0
        self.age = 0
        self.prev_b = 0
        self.result = 0

    def update(self, close):
        if not self.prev_close:
            self.prev_close = close
            return self.result

        delta_close = close - self.prev_close
        self.prev_b = self.b
        if delta_close > 0:
            self.b = 1
        elif delta_close < 0:
            self.b = -1
        else:
            self.b = self.prev_b

        if len(self.b_values) < self.window:
            self.b_values.append(self.b)
            self.b_sum += self.b
        else:
            self.b_sum -= self.b_values[int(self.age)]
            self.b_sum += self.b
            self.b_values[int(self.age)] = self.b
            self.age = (self.age + 1) % self.window
        self.prev_close = close
        return self.result
