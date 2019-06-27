# https://www.tradingview.com/script/mvXfI6Yf-Finite-Impulse-Response-FIR-Filter

from trader.indicator.IndicatorBase import IndicatorBase
from trader.lib.struct.CircularArray import CircularArray

class FIR_Filter(IndicatorBase):
    def __init__(self, c1=1.0, c2=3.5, c3=4.5, c4=3, c5=0.5, c6=-0.5, c7=-1.5):
        IndicatorBase.__init__(self, use_close=True)
        self.window = 7
        self.src = CircularArray(window=7, reverse=True)
        # 7 coefficients
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        self.c5 = c5
        self.c6 = c6
        self.c7 = c7
        self.csum = self.c1 + self.c2 + self.c3 + self.c4 + self.c5 + self.c6 + self.c7
        self.result = 0

    def update(self, close):
        self.src.add(float(close))

        if not self.src.full():
            return self.result

        result = self.c1 * self.src[0]
        result += self.c2 * self.src[1]
        result += self.c3 * self.src[2]
        result += self.c4 * self.src[3]
        result += self.c5 * self.src[4]
        result += self.c6 * self.src[5]
        result += self.c7 * self.src[6]
        self.result = result / self.csum

        return self.result
