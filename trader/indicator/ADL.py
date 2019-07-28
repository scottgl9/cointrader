# Accumulation Distribution Indicator (ADL)
from trader.lib.struct.IndicatorBase import IndicatorBase


class ADL(IndicatorBase):
    def __init__(self):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True, use_volume=True)
        self.result = 0

    def update(self, close, low, high, volume):
        if (high - low) == 0:
            return self.result
        prev_result = self.result

        cmfv = volume * ((close - low) - (high - close)) / (high - low)
        self.result = prev_result + cmfv
        return self.result
