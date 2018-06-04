# My idea to use the quadratic estimation to find maximum point of upward trend

import numpy as np
from numpy import array
from scipy.linalg import solve
from trader.indicator.REMA import REMA
from trader.lib.CircularArray import CircularArray


class QUAD2:
    def __init__(self, window=100):
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.values = CircularArray(window=window)
        self.result = 0.0
        self.age = 0
        self.window = window
        self.rema = REMA(12)

    def update(self, price):
        self.values.add(float(price))

        if len(self.values) < self.window:
            self.age = (self.age + 1) % self.window
            return 0

        #if self.values.age == 0:
        self.compute()

        self.result = self.C #self.A * (self.age ** 2) + self.B * self.age + self.C

        self.age = (self.age + 1) % self.window
        return self.result

    def compute(self):
        if len(self.values) < self.window:
            return 0, 0, 0

        x = np.array(range(0, self.window))
        y = np.array(self.values.values_ordered())
        if len(x) < len(y):
            y = y[1:]
        elif len(x) > len(y):
            x = x[1:]

        self.A, self.B, self.C = np.polyfit(x, y, 2)

        # yest = A * x ** 2 + B * x + C
        return self.A, self.B, self.C
