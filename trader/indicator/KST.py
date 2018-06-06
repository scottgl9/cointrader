# Know Sure Thing (KST) Oscillator indicator
from trader.indicator.SMA import SMA
from trader.indicator.ROC import ROC


class KST(object):
    def __init__(self):
        self.roc1 = ROC(window=10)
        self.roc2 = ROC(window=15)
        self.roc3 = ROC(window=20)
        self.roc4 = ROC(window=30)
        self.rocma1 = SMA(window=10)
        self.rocma2 = SMA(window=10)
        self.rocma3 = SMA(window=10)
        self.rocma4 = SMA(window=15)
        self.signal = SMA(window=9)
        self.result = 0

    def update(self, close):
        result1 = self.rocma1.update(self.roc1.update(float(close)))
        result2 = self.rocma1.update(self.roc2.update(float(close)))
        result3 = self.rocma1.update(self.roc3.update(float(close)))
        result4 = self.rocma1.update(self.roc4.update(float(close)))

        self.result = (result1 * 1.0) + (result2 * 2.0) + (result3 * 3.0) + (result4 * 4.0)
        self.signal.update(self.result)

        return self.result
