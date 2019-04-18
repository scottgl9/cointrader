from .HourlySignalBase import HourlySignalBase
from trader.indicator.LSMA import LSMA

class Hourly_LSMA_Crossover(HourlySignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(Hourly_LSMA_Crossover, self).__init__(accnt, symbol, asset_info)
        self.lsma24 = LSMA(24)
        # 1 week LSMA
        self.lsma168 = LSMA(168)
        # 1 month LSMA
        self.lsma720 = LSMA(720)

    def load(self, klines):
        self.klines = klines

    def process(self):
        for kline in self.klines:
            ts = int(kline['ts'])
            close = float(kline['close'])
            self.lsma24.update(close, ts)
            self.lsma168.update(close, ts)
            self.lsma720.update(close, ts)

