# Standard Deviation (STDDEV) indicator
import numpy as np

class STDDEV:
    def __init__(self, window=20):
        self.result = 0.0
        self.last_result = 0.0
        self.window = window
        self.values = []
        self.age = 0
        self.sum = 0.0

    def ready(self):
        return len(self.values) == self.window

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))
            self.sum += float(value)
        else:
            tail = self.values[int(self.age)]
            self.values[int(self.age)] = float(value)
            self.sum += float(value) - tail

            mean_value = self.sum / float(self.window)
            result = 0.0
            for value in self.values:
                result += (value - mean_value) * (value - mean_value)

            self.result = np.sqrt(result / float(self.window))

        self.age = (self.age + 1) % self.window

        return self.result
