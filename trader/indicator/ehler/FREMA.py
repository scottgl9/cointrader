# Forward Reverse EMA (FREMA)
# https://www.prorealcode.com/prorealtime-indicators/john-ehlers-forward-reverse-ema/
import numpy as np
from trader.lib.CircularArray import CircularArray

class FREMA(object):
    def __init__(self):
        self.AA = 0.1
        self.CC = 1 - self.AA
        self.result = 0
        self.RE1 = CircularArray(window=3, reverse=True, dne=0)
        self.RE2 = CircularArray(window=3, reverse=True, dne=0)
        self.RE3 = CircularArray(window=3, reverse=True, dne=0)
        self.RE4 = CircularArray(window=3, reverse=True, dne=0)
        self.RE5 = CircularArray(window=3, reverse=True, dne=0)
        self.RE6 = CircularArray(window=3, reverse=True, dne=0)
        self.RE7 = CircularArray(window=3, reverse=True, dne=0)
        self.RE8 = CircularArray(window=3, reverse=True, dne=0)
        self.EMA = CircularArray(window=3, reverse=True, dne=0)
        self.Signal = CircularArray(window=3, reverse=True, dne=0)
        self.count = 0

    def update(self, close):
        self.EMA.add(self.AA * float(close) + self.CC * self.EMA[1])
        if len(self.EMA) < self.EMA.window:
            return self.result

        self.RE1.add(self.CC * self.EMA[0] + self.EMA[1])
        self.RE2.add(np.exp(2 * np.log(self.CC)) * self.RE1[0] + self.RE1[1])
        self.RE3.add(np.exp(4 * np.log(self.CC)) * self.RE2[0] + self.RE2[1])
        self.RE4.add(np.exp(8 * np.log(self.CC)) * self.RE3[0] + self.RE3[1])
        self.RE5.add(np.exp(16 * np.log(self.CC)) * self.RE4[0] + self.RE4[1])
        self.RE6.add(np.exp(32 * np.log(self.CC)) * self.RE5[0] + self.RE5[1])
        self.RE7.add(np.exp(64 * np.log(self.CC)) * self.RE6[0] + self.RE6[1])
        self.RE8.add(np.exp(128 * np.log(self.CC)) * self.RE7[0] + self.RE7[1])
        self.Signal.add(self.EMA[0] - self.AA * self.RE8[0])

        # indicator doesn't propagate all values through to self.Signal until 2^7 = 128 updates
        if self.count < 128:
            self.count += 1
            self.result = 0
        else:
            self.result = self.Signal[0]

        return self.result
