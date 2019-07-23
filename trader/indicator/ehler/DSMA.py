# Deviation Scaled Moving Average (DSMA)
# https://www.prorealcode.com/prorealtime-indicators/deviation-scaled-moving-average-dsma/
# The DSMA is an adaptive moving average that features rapid adaptation to volatility in price movement.
# It accomplishes this adaptation by modifying the alpha term of an EMA byt he amplitude of an oscillator scaled
# in standard deviations from the mean. The DSMA's responsiveness can be changed by using different values
# for the input parameter period.
from trader.lib.struct.IndicatorBase import IndicatorBase
import numpy as np
from trader.lib.struct.CircularArray import CircularArray

class DSMA(IndicatorBase):
    def __init__(self, period=40):
        IndicatorBase.__init__(self, use_close=True)
        self.period = period
        self.closes = CircularArray(window=3, reverse=True, dne=0)
        self.zeros = CircularArray(window=3, reverse=True, dne=0)
        self.filt = CircularArray(window=self.period, reverse=True, dne=0)
        self.DSMA = CircularArray(window=self.period, reverse=True, dne=0)
        self.result = 0
        # Smooth with a Super Smoother
        self.a1 = np.exp(-1.414 * 3.14159 / (0.5 * self.period))
        self.b1 = 2.0 * self.a1 * np.cos(1.414 * 180.0 / (0.5 * self.period))
        self.c2 = self.b1
        self.c3 = -self.a1 * self.a1
        self.c1 = 1.0 - self.c2 - self.c3

    def update(self, close):
        self.closes.add(float(close))

        self.zeros.add(self.closes[0] - self.closes[2])

        self.filt.add(self.c1*(self.zeros[0] + self.zeros[1]) / 2 + self.c2*self.filt[1] + self.c3*self.filt[2])

        RMS = 0
        for count in range(0, self.period - 1):
            RMS = RMS + self.filt[count] * self.filt[count]
 
        RMS = np.sqrt(RMS / self.period)

        #Rescale Filt in terms of Standard Deviations
        ScaledFilt = self.filt[0] / RMS
        alpha1 = np.abs(ScaledFilt) * 5 / self.period
        self.DSMA.add(alpha1 * self.closes[0] + (1 - alpha1) * self.DSMA[1])

        if len(self.DSMA) == self.DSMA.window:
            self.result = self.DSMA[0]

        return self.result
