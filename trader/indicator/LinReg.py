# Linear Regression (for moving average)
import numpy as np
from trader.indicator.EMA import EMA


class LinReg(object):
    def __init__(self, window=50):
        self.window = window
        self.result = 0.0
        self.slope = 0.0
        self.start_value = 0.0
        self.last_start_value = 0.0
        self.last_end_value = 0.0
        self.age = 0
        self.age_offset = 0
        self.A = self.B = self.C = 0
        self.values = []
        self.xvalues = []
        self.ema = EMA(3)

    def basic_linear_regression(self, x, y):
        # Basic computations to save a little time.
        length = len(x)
        sum_x = sum(x)
        sum_y = sum(y)

        sum_x_squared = sum(map(lambda a: a * a, x))
        sum_of_products = sum([x[i] * y[i] for i in range(length)])

        # Magic formulae!
        a = (sum_of_products - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
        b = (sum_y - a * sum_x) / length
        return a, b

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))
            self.xvalues.append(self.age)
            if len(self.values) < 3:
                self.result = float(value)
                self.age = (self.age + 1) % self.window
                return self.result
        else:
            self.values[int(self.age)] = float(value)

        #self.A, self.B = self.basic_linear_regression(self.xvalues, self.values)

        if self.age % self.window == 0:
            result = np.polyfit(np.array(self.xvalues), np.array(self.values), deg=2)
            if result[2] > 0:
                self.A = result[0]
                self.B = result[1]
                self.C = result[2]

        self.result = self.A * self.age ** 2 + self.B * self.age + self.C
        #self.result = self.B

        self.age = (self.age + 1) % self.window

        return self.result
