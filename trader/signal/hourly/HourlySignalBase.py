class HourlySignalBase(object):
    def __init__(self, accnt=None, symbol=None, asset_info=None):
        self.accnt = accnt
        self.symbol = symbol
        self.asset_info = asset_info
        self.klines = None

    def load(self, klines):
        pass

    def process(self):
        pass
