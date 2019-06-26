from trader.indicator.EMA import EMA
from trader.indicator.AEMA import AEMA
from trader.indicator.MovingMedian import MovingMedian
from .MTS_LSMA import MTS_LSMA


class MTS_SlidingBoxes(object):
    def __init__(self):
        self.ema = AEMA(win=5, scale_interval_secs=60)
        self.ema2 = AEMA(win=25, scale_interval_secs=60)
        self.mts_lsma = MTS_LSMA(win_secs=90)
        self.result = 0
        self.result2 = 0

    def update(self, close, ts):
        self.ema.update(close, ts)
        self.ema2.update(close, ts)
        self.mts_lsma.update(close, ts)
        self.result = self.ema.result
        self.result2 = self.ema2.result
        return self.result, self.result2
