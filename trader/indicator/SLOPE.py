# simple moving slope indicator
class SLOPE(object):
    def __init__(self, window=50):
        self.window = window
        self.values = []
        self.age = 0
        self.result = 0

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))
        else:
            old_value = self.values[int(self.age)]
            self.values[int(self.age)] = float(value)
            self.result = (float(value) - old_value) / self.window

        self.age = (self.age + 1) % self.window

        return self.result
