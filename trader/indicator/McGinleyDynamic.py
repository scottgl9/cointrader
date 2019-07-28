# McGinley Dynamic Indicator
from trader.lib.struct.IndicatorBase import IndicatorBase


class McGinleyDynamic(IndicatorBase):
    def __init__(self, win, k=0.6, scale=1.0):
        IndicatorBase.__init__(self, use_close=True)
        self.win = win
        self.k = k
        self.s = scale
        self.result = 0

    def update(self, close):
        if not self.result:
            self.result = close
            return self.result

        prev_result = self.result

        self.result = prev_result + (close - prev_result) / (self.k * self.win * self.s * (close / prev_result) ** 4)
        return self.result
