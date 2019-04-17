from .HourlySignalBase import HourlySignalBase

class Hourly_LSMA_Crossover(HourlySignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        super(Hourly_LSMA_Crossover).__init__(accnt, symbol, asset_info)

    def load(self, klines):
        self.klines = klines

    def process(self):
        pass
