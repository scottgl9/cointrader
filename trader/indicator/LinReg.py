# Linear Regression (for moving average)
import numpy as np
from trader.indicator.EMA import EMA


class LinReg(object):
    def __init__(self, window=12):
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

    def update(self, value):
        if len(self.values) < self.window:

            self.values.append(float(value))
            self.xvalues.append(self.age)
            if len(self.values) < 3:
                self.age = (self.age + 1) % self.window
                self.result = float(value)
                return self.result
        else:
            self.values[int(self.age)] = float(value)

            age = (self.age + 1) % self.window
            self.xvalues = []
            while age != self.age:
                self.xvalues.append(age)
                age = (age + 1) % self.window

            self.xvalues.append(self.age)

        result = np.polyfit(np.array(self.xvalues), np.array(self.values), deg=2)
        if result[2] > 0:
            self.A = result[0]
            self.B = result[1]
            self.C = result[2]
            print(self.A, self.B, self.C)

        self.result = self.ema.update(self.A * self.age ** 2 + self.B * self.age + self.C)

        self.age = (self.age + 1) % self.window

        return self.result
