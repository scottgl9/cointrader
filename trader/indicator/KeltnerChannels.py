# Keltner Channels Indicator
# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:keltner_channels

from .IndicatorBase import IndicatorBase
from .ATR import ATR
from .EMA import EMA


class KeltnerChannels(IndicatorBase):
    def __init__(self, ema_win=20, atr_win=10):
        IndicatorBase.__init__(self, use_close=True, use_low=True, use_high=True)
        self.ema_win = ema_win
        self.atr_win = atr_win
        self.atr = ATR(self.atr_win)
        self.ema = EMA(self.ema_win)
        self.upper = 0
        self.middle = 0
        self.lower = 0

    def update(self, close, low, high):
        self.ema.update(close)
        self.atr.update(self.ema.result, low, high)

        if not self.atr.result:
            return self.upper, self.middle, self.lower

        self.middle = self.ema.result
        self.upper = self.middle + (2.0 * self.atr.result)
        self.lower = self.middle - (2.0 * self.atr.result)

        return self.upper, self.middle, self.lower
