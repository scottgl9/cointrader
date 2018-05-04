# My idea to use the quadratic estimation to find maximum point of upward trend

import numpy as np
from numpy import array
from scipy.linalg import solve


class QUAD:
    def __init__(self, window=1000):
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.prices = []
        self.result = 0.0
        self.age = 0
        self.window = window

    def update(self, price):
        if len(self.prices) < self.window:
            self.prices.append(float(price))
        else:
            self.prices[int(self.age)] = float(price)

            if self.age == 0:
                self.compute()

            self.result = self.A * (self.age ** 2) + self.B * self.age + self.C

        self.age = (self.age + 1) % self.window
        return self.result

    def compute(self):
        if len(self.prices) < self.window:
            return 0, 0, 0

        x = np.array(range(self.window, self.window * 2))
        y = np.array(self.prices)
        if len(x) < len(y):
            y = y[1:]
        elif len(x) > len(y):
            x = x[1:]
        N = len(y)

        #try:
        #    x4 = (x ** 4).sum()
        #    x3 = (x ** 3).sum()
        #    x2 = (x ** 2).sum()
        #    M = array([[x4, x3, x2], [x3, x2, x.sum()], [x2, x.sum(), N]])
        #    K = array([(y * x ** 2).sum(), (y * x).sum(), y.sum()])
        #    self.A, self.B, self.C = solve(M, K)
        #except:
        #    return 0.0, 0.0, 0.0
        self.A, self.B, self.C = np.polyfit(x, y, 2)
        print(self.A, self.B, self.C)

        # yest = A * x ** 2 + B * x + C
        return self.A, self.B, self.C
