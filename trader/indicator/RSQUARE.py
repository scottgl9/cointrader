# R-Squared Index
import numpy as np


class RSQUARE(object):
    def __init__(self, window=100):
        self.window = window
        self.values = []
        self.age = 0
        self.result = 0
        self.Y = np.array(range(0, self.window))
        self.yvar = np.mean(self.Y * self.Y) - np.mean(self.Y) ** 2

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))
        else:
            self.values[int(self.age)] = float(value)
            X = np.array(self.values)
            xvar = np.mean(X * X) - np.mean(X) ** 2
            covar = np.mean(X * self.Y) - (np.mean(X) * np.mean(self.Y))

            if xvar == 0:
                self.result = 0
            else:
                self.result = covar / (xvar * self.yvar)

        self.age = (self.age + 1) % self.window

        return self.result
