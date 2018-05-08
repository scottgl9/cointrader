# Weighted Moving Average


class WMA(object):
    def __init__(self, window, scale=1.0):
        self.values = []
        self.window = window
        self.scale = scale
        self.age = 0
        self.result = 0

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))

            if len(self.values) == 1:
                self.result = float(value)
                self.age = (self.age + 1) % self.window
                return self.result

            sum1 = sum2 = 0
            for i in (0, len(self.values) - 1):
                sum1 += self.values[i] * (i + 1) * self.scale
                sum2 += (i + 1) * self.scale
            self.result = float(sum1) / float(sum2)
        else:
            self.values[int(self.age)] = float(value)

            sum1 = sum2 = 0
            pos = (self.age + 1) % self.window
            weight = 1

            while pos != self.age:
                sum1 += self.values[int(pos)] * weight * self.scale
                sum2 += weight * self.scale
                pos = (pos + 1) % self.window
                weight += 1

            self.result = float(sum1) / float(sum2)

        self.age = (self.age + 1) % self.window

        return self.result
