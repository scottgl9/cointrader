# a second order low pass filter
from trader.lib.CircularArray import CircularArray

class LowPass:
    def __init__(self, period):
        self.period = period
        self.Price = CircularArray(window=3, dne=0, reverse=True)
        self.LP = CircularArray(window=3, dne=0, reverse=True)
        self.result = 0
        self.counter = 0

    def update(self, close):
        self.Price.add(float(close))

        if not self.Price.full():
            self.LP.add(float(close))
            return self.result

        a = 2.0 / (1 + self.period)

        self.LP.add((a - 0.25 * a * a) * self.Price[0]
        + 0.5 * a * a * self.Price[1]
        - (a - 0.75 * a * a) * self.Price[2]
        + 2 * (1. - a) * self.LP[1]
        - (1. - a) * (1. - a) * self.LP[2])

        self.result = self.LP[0]

        return self.result
