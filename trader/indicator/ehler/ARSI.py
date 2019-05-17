# Adaptive Relative Strength Index (RSI)
# Rocket Science for Traders: Digital Signal Processing Applications
# https://www.prorealcode.com/prorealtime-indicators/john-ehlers-adaptive-rsi/
from trader.indicator.IndicatorBase import IndicatorBase
import numpy as np
from trader.lib.struct.CircularArray import CircularArray


class ARSI(IndicatorBase):
    def __init__(self):
        IndicatorBase.__init__(self, use_close=True)
        self.CycPart = .5
        self.result = 0
        self.Close = CircularArray(26)
        self.Price = CircularArray(4)
        self.Smooth = CircularArray(7)
        self.Detrender = CircularArray(7)
        self.Period = 0
        self.Period1 = 0 # last period
        self.SmoothPeriod = 0
        self.SmoothPeriod1 = 0 # last SmoothPeriod
        self.Q1 = CircularArray(7)
        self.I1 = CircularArray(7)
        self.Q2 = CircularArray(3)
        self.I2 = CircularArray(3)
        self.Re = CircularArray(3)
        self.Im = CircularArray(3)

    def update(self, price):
        self.Price.add(float(price))
        self.Close.add(float(price))
        self.Smooth.add((4*self.Price[0] + 3*self.Price[1] + 2*self.Price[2] + self.Price[3]) / 10)
        self.Detrender.add((.0962*self.Smooth[0] + .5769*self.Smooth[2] - .5769*self.Smooth[4] - .0962*self.Smooth[6])*(.075*self.Period1 + .54))

        # Compute InPhase and Quadrature components
        self.Q1.add((.0962 * self.Detrender[0] + .5769 * self.Detrender[2] - .5769 * self.Detrender[4] - .0962 * self.Detrender[6]) * (.075 * self.Period1 + .54))
        self.I1.add(self.Detrender[3])

        # Advance the phase of I1 and Q1 by 90 degrees
        j1 = (.0962 * self.I1[0] + .5769 * self.I1[2] - .5769 * self.I1[4] - .0962 * self.I1[6]) * (.075 * self.Period1 + .54)
        jQ = (.0962 * self.Q1[0] + .5769 * self.Q1[2] - .5769 * self.Q1[4] - .0962 * self.Q1[6]) * (.075 * self.Period1 + .54)

        # Phasor addition for 3 bar averaging
        self.I2.add(self.I1[0] - jQ)
        self.Q2.add(self.Q1[0] + j1)

        # Smooth the I and Q components before applying the discriminator
        self.I2.add(.2 * self.I2[0] + .8 * self.I2[1])
        self.Q2.add(.2 * self.Q2[0] + .8 * self.Q2[1])

        # Homodyne Discriminator
        self.Re.add(self.I2[0] * self.I2[1] + self.Q2[0] * self.Q2[1])
        self.Im.add(self.I2[0] * self.Q2[1] - self.Q2[0] * self.I2[1])
        self.Re.add(.2 * self.Re[0] + .8 * self.Re[1])
        self.Im.add(.2 * self.Im[0] + .8 * self.Im[1])


        if self.Im[0] != 0 and self.Re[0] != 0:
            self.Period = 360 / np.arctan(self.Im[0] / self.Re[0])
        if self.Period > 1.5 * self.Period1:
            self.Period = 1.5 * self.Period1
        if self.Period < .67 * self.Period1:
            self.Period = .67 * self.Period1

        if self.Period < 6:
            self.Period = 6
        if self.Period > 50:
            self.Period = 50

        Period = .2 * self.Period + .8 * self.Period1
        self.Period = Period
        self.SmoothPeriod = .33 * self.Period + .67 * self.SmoothPeriod1

        CU = 0
        CD = 0
        for count in range(0, np.rint(self.CycPart * self.SmoothPeriod) - 1):
            if self.Close[count] - self.Close[count + 1] > 0:
                CU = CU + (self.Close[count] - self.Close[count + 1])
            if self.Close[count] - self.Close[count + 1] < 0:
                CD = CD + (self.Close[count + 1] - self.Close[count])

        if CU + CD != 0:
            self.result = 100 * CU / (CU + CD)

        self.Period1 = self.Period
        self.SmoothPeriod1 = self.SmoothPeriod

        return self.result
