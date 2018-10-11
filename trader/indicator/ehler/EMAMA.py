# https://www.prorealcode.com/prorealtime-indicators/john-ehlers-mama-the-mother-of-adaptive-moving-average/
# Ehler's MESA Adaptive Moving Average
import numpy as np
from trader.lib.CircularArray import CircularArray

class EMAMA(object):
    def __init__(self, fast_limit=0.5, slow_limit=0.05):
        self.FastLimit = fast_limit
        self.SlowLimit = slow_limit
        self.Price = CircularArray(window=5, dne=0, reverse=True)
        self.Smooth = CircularArray(window=7, dne=0, reverse=True)
        self.Detrender = CircularArray(window=7, dne=0, reverse=True)
        self.I1 = CircularArray(window=7, dne=0, reverse=True)
        self.Q1 = CircularArray(window=7, dne=0, reverse=True)
        self.I2 = CircularArray(window=3, dne=0, reverse=True)
        self.Q2 = CircularArray(window=3, dne=0, reverse=True)
        self.Period = CircularArray(window=3, dne=0, reverse=True)
        self.SmoothPeriod = CircularArray(window=3, dne=0, reverse=True)
        self.Phase = CircularArray(window=3, dne=0, reverse=True)
        self.MAMA = CircularArray(window=3, dne=0, reverse=True)
        self.FAMA = CircularArray(window=3, dne=0, reverse=True)

    def update(self, close):
        self.Price.add(float(close))

        self.Smooth.add((4 * self.Price[0] + 3 * self.Price[1] + 2 * self.Price[2] + self.Price[3]) / 10)
        self.Detrender.add((.0962 * self.Smooth[0] + .5769 * self.Smooth[2] - .5769 * self.Smooth[4] - .0962 * self.Smooth[6]) * (
                    .075 * self.Period[1] + .54))

        self.Q1.add((.0962 * self.Detrender[0] + .5769 * self.Detrender[2] - .5769 * self.Detrender[4] - .0962 * self.Detrender[6]) * (
                    .075 * self.Period[1] + .54))
        self.I1.add(self.Detrender[3])

        jI = (.0962 * self.I1[0] + .5769 * self.I1[2] - .5769 * self.I1[4] - .0962 * self.I1[6]) * (.075 * self.Period[1] + .54)
        jQ = (.0962 * self.Q1[0] + .5769 * self.Q1[2] - .5769 * self.Q1[4] - .0962 * self.Q1[6]) * (.075 * self.Period[1] + .54)

        self.I2.add(self.I1[0] - jQ)
        self.Q2.add(self.Q1[0] + jI)

        self.I2.add(.2 * self.I2[0] + .8 * self.I2[1])
        self.Q2.add(.2 * self.Q2[0] + .8 * self.Q2[1])

        Re = self.I2[0] * self.I2[1] + self.Q2[0] * self.Q2[1]
        Im = self.I2[0] * self.Q2[1] - self.Q2[0] * self.I2[1]
        Re = .2 * Re[0] + .8 * Re[1]
        Im = .2 * Im[0] + .8 * Im[1]

        if Im != 0 and Re != 0:
            self.Period.add(360 / np.arctan(Im / Re))

        if self.Period[0] > 1.5 * self.Period[1]:
            self.Period[0] = 1.5 * self.Period[1]

        if self.Period[0] < 0.67 * self.Period[1]:
            self.Period[0] = 0.67 * self.Period[1]

        if self.Period[0] < 6:
            self.Period[0] = 6
        if self.Period[0] > 50:
            self.Period[0] = 50

        self.Period.add(.2 * self.Period[0] + .8 * self.Period[1])
        self.SmoothPeriod.add(.33 * self.Period[0] + .67 * self.SmoothPeriod[1])

        if self.I1[0] != 0:
            self.Phase.add(np.arctan(self.Q1[0] / self.I1[0]))

        DeltaPhase = self.Phase[1] - self.Phase[0]

        if DeltaPhase < 1:
            DeltaPhase = 1

        alpha = self.FastLimit / DeltaPhase

        if alpha < self.SlowLimit:
            alpha = self.SlowLimit

        self.MAMA.add(alpha * self.Price[0] + (1 - alpha) * self.MAMA[1])
        self.FAMA.add(.5 * alpha * self.MAMA[0] + (1 - .5 * alpha) * self.FAMA[1])
