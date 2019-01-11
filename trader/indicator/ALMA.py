# Arnaud Legoux Moving Average (ALMA)
import numpy as np

class ALMA(object):
    def __init__(self, window=9, sigma=6, offset=0.85):
        self.window = window
        self.sigma = sigma
        self.offset = offset
        self.prices = []
        self.age = 0
        self.result = 0

    def update(self, price, ts=0):
        if len(self.prices) < self.window:
            self.prices.append(float(price))
            return self.result

        self.prices[int(self.age)] = float(price)

        m = (self.offset * (self.window - 1))
        s = self.window / self.sigma

        WtdSum = 0
        CumWt = 0

        for k in range(0, self.window - 1):
            Wtd = np.exp(-((k-m)*(k-m))/(2*s*s))
            WtdSum += Wtd * self.prices[self.window - 1 - k]
            CumWt += Wtd

        self.result = WtdSum / CumWt

        return self.result
