# Tick imbalance bars (TIB)

class TIB(object):
    def __init__(self, window):
        self.window = window
        self.prev_close = 0
        self.b = 0
        self.b_values = []
        self.b_sum = 0
        self.b_ewma = 0
        self.b_up = 0
        self.b_down = 0
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
            if self.b == 1:
                self.b_up += 1
            elif self.b == -1:
                self.b_down += 1
        else:
            prev_b = self.b_values[int(self.age)]
            if prev_b == 1:
                self.b_up -= 1
            elif prev_b == -1:
                self.b_down -= 1
            if self.b == 1:
                self.b_up += 1
            elif self.b == -1:
                self.b_down += 1
            self.b_sum -= prev_b
            self.b_sum += self.b
            self.b_values[int(self.age)] = self.b
            self.result = self.b_sum
            self.age = (self.age + 1) % self.window
        self.prev_close = close
        return self.result
