# John Ehler's Instantaneous Trendline
# https://c.mql5.com/forextsd/forum/59/023inst.pdf
# https://www.prorealcode.com/prorealtime-indicators/john-ehlers-instantaneous-trendline/
import numpy as np
from trader.lib.CircularArray import CircularArray

class InstantTrendline(object):
    def __init__(self, window=40):
        self.window = window
        self.prices = CircularArray(window=8, reverse=True, dne=0)
        self.value3 = CircularArray(window=5, reverse=True, dne=0)
        self.Inphase = CircularArray(window=4, reverse=True, dne=0)
        self.Quadrature = CircularArray(window=3, reverse=True, dne=0)
        self.DeltaPhase = CircularArray(window=self.window, reverse=True, dne=0)
        self.value5 = CircularArray(window=3, reverse=True, dne=0)
        self.value11 = CircularArray(window=3, reverse=True, dne=0)
        self.last_phase = 0
        self.phase = 0
        self.instperiod = 0
        self.last_instperiod = 0
        self.result = 0
        self.Imult = 0.635
        self.Qmult = 0.338
        self.barindex = 0


    def update(self, price):
        self.prices.add(float(price))

        if len(self.prices) < self.window:
            return self.result

        self.value3.add(self.prices[0] - self.prices[7])

        if len(self.value3) < self.value3.window:
            return self.result

        # Compute InPhase and Quadrature components
        self.Inphase.add(1.25 * self.value3[4] - self.Imult * self.value3[2] + self.Imult * self.Inphase[3])
        self.Quadrature.add(self.value3[2] - self.Qmult * self.value3[0] + self.Qmult * self.Quadrature[2])

        if len(self.Inphase) < self.Inphase.window or len(self.Quadrature) < self.Quadrature.window:
            return self.result

        # Use ArcTangent to compute the current phase
        if abs(self.Inphase[0] + self.Inphase[1]) > 0:
            a = np.abs((self.Quadrature[0] + self.Quadrature[1]) / self.Inphase[0] + self.Inphase[1])
            Phase = np.arctan(a)

        # Resolve the ArcTangent ambiguity
        if self.Inphase[0] < 0 and self.Quadrature[0] > 0:
            Phase = 180 - Phase
        if self.Inphase[0] < 0 and self.Quadrature[0] < 0:
            Phase = 180 + Phase
        if self.Inphase[0] > 0 and self.Quadrature[0] < 0:
            Phase = 360 - Phase

        self.last_phase = self.phase
        self.phase = Phase

        # Compute a differential phase, resolve phase wraparound, and limit delta phase errors
        deltaPhase = self.last_phase - self.phase               #Phase[1] - Phase
        if self.last_phase < 90 and self.phase > 270:           #Phase[1] < 90 and Phase > 270:
            deltaPhase = 360 + self.last_phase - self.phase     #Phase[1] - Phase
        if deltaPhase < 7:
            deltaPhase = 7
        if deltaPhase > 60:
            deltaPhase = 60

        self.DeltaPhase.add(deltaPhase)

        # Sum DeltaPhases to reach 360 degrees. The sum is the instantaneous period.
        self.last_instperiod = self.instperiod
        self.instperiod = 0
        Value4 = 0
        for count in range(0, 40):
            Value4 = Value4 + self.DeltaPhase[count]
            if Value4 > 360 and self.instperiod == 0:
                self.instperiod = count

        # Resolve Instantaneous Period errors and smooth
        if self.instperiod == 0:
            self.instperiod = self.last_instperiod

        self.value5.add(0.25 * self.instperiod + .75 * self.value5[1])

        # Compute Trendline as simple average over the measured dominant cycle period
        Period = int(np.rint(self.value5[0])) # ROUND(Value5)
        Trendline = 0
        for count in range(0, Period + 1):
            Trendline = Trendline + self.prices[count]

        if Period > 0:
            Trendline = Trendline / (Period + 2)

        self.value11.add(0.33 * (self.prices[0] + 0.5 * (self.prices[0] - self.prices[3])) + 0.67 * self.value11[1])

        #if len(self.value11) == self.value11.window:
        self.result = self.value11[0]

        #if self.barindex < 26:
        #    Trendline = Price
        #    Value11 = Price

        # Return Trendline as "TR", Value11 as "ZL"

        return self.result
