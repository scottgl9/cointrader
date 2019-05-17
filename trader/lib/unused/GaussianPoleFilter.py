# https://www.tradingview.com/script/MxgNScFI-NG-Gaussian-Filter-Multi-Pole/
# NOTE: incomplete
import numpy as np
from trader.lib.struct.CircularArray import CircularArray

class GaussianPoleFilter(object):
    def __init__(self, lag=13, poles=8):
        self.beta = (1 - np.cos(2 * np.pi / lag)) / (pow(np.sqrt(2), 2.0 / poles) - 1)
        self.alfa = -self.beta + np.sqrt(self.beta * self.beta + 2.0 * self.beta)
        self.pre_pow = pow(self.alfa, poles)
        self.lag = lag
        self.poles = poles
        self.filter = CircularArray(window=poles, reverse=False, dne=0)

    def fact(self, num):
        return np.math.factorial(num)

    def get_poles(self, f, n):
        filt = f
        sign = 1
        results = 0 + n # tv series spoofing
        for r in range(1, max(min(self.poles, n), 1)):
            mult = self.fact(self.poles) / (self.fact(self.poles - r) * self.fact(r))
            matPo = pow(1 - self.alfa, r)
            prev = filt[r - 1]
            sum = sign * mult * matPo * prev
            results = results + sum
            sign = sign * -1
        return results - n

    def update(self, price):
        if self.filter.empty():
            self.filter.add(float(price) * self.pre_pow)
        else:
            pre = float(price) * self.pre_pow
        #result = n > 0 ?  getPoles(filter[1]): 0
        #filter:= pre + result
