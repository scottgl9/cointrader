# My idea to use the quadratic estimation to find maximum point of upward trend

import numpy as np
from numpy import array
from scipy.linalg import solve

class QUAD:
    def __init__(self, window=30.0):
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.prices = []
        self.timestamps = []
        self.result = 0.0
        self.age = 0
        self.start_age = -1
        self.window = window
        self.ts_age = int(window)

    #timestamp_max = initial_time + 60.0 * (-B / (2 * A))
    #timestamp_current = initial_time + i * 60.0

    def update(self, price, timestamp=0):
        if len(self.prices) < self.window:
            self.prices.append(float(price))
            self.timestamps.append(self.ts_age) #float(timestamp))
            self.start_age = 0
        else:
            self.prices[int(self.age)] = float(price)
            self.timestamps[int(self.age)] = self.ts_age #* 60.0#float(timestamp)
            self.start_age = (self.age + 2) % self.window

        self.age = (self.age + 1) % self.window
        self.ts_age += 1
        # points to the oldest price and timestamp
        return self.ts_age

    def adjust_timestamps(self, timestamps):
        min_ts = min(timestamps)
        for i in range(0, len(timestamps)):
            timestamps[i] -= min_ts
        return timestamps

    def compute(self):
        if len(self.timestamps) < self.window:
            return 0, 0, 0
        timestamps = self.adjust_timestamps(self.timestamps)

        x = np.array(timestamps)
        y = np.array(self.prices)
        if len(x) < len(y):
            y = y[1:]
        elif len(x) > len(y):
            x = x[1:]
        N = len(y)

        try:
            x4 = (x ** 4).sum()
            x3 = (x ** 3).sum()
            x2 = (x ** 2).sum()
            M = array([[x4, x3, x2], [x3, x2, x.sum()], [x2, x.sum(), N]])
            K = array([(y * x ** 2).sum(), (y * x).sum(), y.sum()])
            self.A, self.B, self.C = solve(M, K)
        except:
            return 0.0, 0.0, 0.0

        #print(self.A, self.B, self.C)

        # yest = A * x ** 2 + B * x + C
        return self.A, self.B, self.C
