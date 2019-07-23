from trader.lib.struct.IndicatorBase import IndicatorBase
from math import log10


class OBV(IndicatorBase):
    def __init__(self, use_log10=False):
        IndicatorBase.__init__(self, use_close=True, use_volume=True)
        self.use_log10 = use_log10
        self.result = 0.0
        self.last_result = 0.0
        self.last_close = 0.0

    def update(self, close, volume):
        if self.use_log10:
            if float(volume) != 0:
                volume = log10(float(volume))
        self.last_result = self.result
        if self.result == 0:
            self.result = float(volume)
            self.last_close = close
            return self.result

        if close > self.last_close:
            self.result += float(volume)
        elif close < self.last_close:
            self.result -= float(volume)

        self.last_close = close

        return self.result
