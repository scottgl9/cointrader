# John Ehler's Instantaneous Trendline
# https://c.mql5.com/forextsd/forum/59/023inst.pdf
# https://www.prorealcode.com/prorealtime-indicators/john-ehlers-instantaneous-trendline/
import numpy as np
from trader.lib.CircularArray import CircularArray

class InstantTrendline(object):
    def __init__(self, window=8):
        self.window = window
        self.prices = CircularArray(window=self.window)
        self.value3 = CircularArray(window=5)
        self.Inphase = CircularArray(window=4)
        self.Quadrature = CircularArray(window=3)
        self.result = 0
        self.Imult = 0.635
        self.Qmult = 0.338


    def update(self, price):
        self.prices.add(float(price))

        if len(self.prices) < self.window:
            return self.result

        self.value3.add(self.prices.last() - self.prices.last(7))

        if len(self.value3) < 5:
            return self.result

        if len(self.Inphase) < 4:
            self.Inphase.add(1.25 * self.value3.last(4) - self.Imult * self.value3.last(2))
        else:
            self.Inphase.add(1.25 * self.value3.last(4) - self.Imult * self.value3.last(2) + self.Imult * self.Inphase.last(3))

        if len(self.Quadrature) < 3:
            self.Quadrature.add(self.value3.last(2) - self.Qmult * self.value3.last())
        else:
            self.Quadrature.add(self.value3.last(2) - self.Qmult * self.value3.last() + self.Qmult * self.Quadrature.last(2))

        if len(self.Inphase) > 2 and abs(self.Inphase.last() + self.Inphase.last(1)):
            a = np.abs((self.Quadrature.last() + self.Quadrature.last(1)) / self.Inphase.last() + self.Inphase.last(1))
            Phase = np.arctan(a)
        else:
            return self.result

        # Resolve the ArcTangent ambiguity
        if self.Inphase.last() < 0 and self.Quadrature.last() > 0:
            Phase = 180 - Phase
        if self.Inphase.last() < 0 and self.Quadrature.last() < 0:
            Phase = 180 + Phase
        if self.Inphase.last() > 0 and self.Quadrature.last() < 0:
            Phase = 360 - Phase
