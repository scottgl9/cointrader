# Know Sure Thing (KST) Oscillator indicator
from .IndicatorBase import IndicatorBase
from trader.indicator.SMA import SMA
from trader.indicator.EMA import EMA
from trader.indicator.ROC import ROC


class KST(IndicatorBase):
    def __init__(self, use_ema=False, scale=1.0):
        IndicatorBase.__init__(self, use_close=True)
        self.roc1 = ROC(window=10)
        self.roc2 = ROC(window=15)
        self.roc3 = ROC(window=20)
        self.roc4 = ROC(window=30)
        if use_ema:
            self.rocma1 = EMA(weight=10, scale=scale)
            self.rocma2 = EMA(weight=10, scale=scale)
            self.rocma3 = EMA(weight=10, scale=scale)
            self.rocma4 = EMA(weight=15, scale=scale)
            self.signal = EMA(weight=9, scale=scale)
        else:
            self.rocma1 = SMA(window=10)
            self.rocma2 = SMA(window=10)
            self.rocma3 = SMA(window=10)
            self.rocma4 = SMA(window=15)
            self.signal = SMA(window=9)
        self.result = 0
        self.signal_result = 0


    def update(self, close, ts=0):
        result1 = self.rocma1.update(self.roc1.update(float(close)))
        result2 = self.rocma2.update(self.roc2.update(float(close)))
        result3 = self.rocma3.update(self.roc3.update(float(close)))
        result4 = self.rocma4.update(self.roc4.update(float(close)))

        self.result = (result1 * 1.0) + (result2 * 2.0) + (result3 * 3.0) + (result4 * 4.0)
        self.signal_result = self.signal.update(self.result)

        return self.result
