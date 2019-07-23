# combined DTWMA/EMA indicator: result = EMA(DTWMA(value))
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.DTWMA import DTWMA
from trader.indicator.EMA import EMA


class DTWMA_EMA(IndicatorBase):
    def __init__(self, dtwma_win, ema_win, scale=1):
        IndicatorBase.__init__(self, use_close=True, use_ts=True)
        self.dtwma_win = dtwma_win
        self.ema_win = ema_win
        self.scale = scale
        self.dtwma = DTWMA(window=self.dtwma_win)
        self.ema = EMA(ema_win, scale=self.scale)
        self.result = 0

    def update(self, value, ts=0):
        result = self.dtwma.update(value, ts)
        self.result = self.ema.update(result, ts)
        return self.result
