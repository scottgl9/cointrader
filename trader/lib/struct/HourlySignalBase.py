class HourlySignalBase(object):
    def __init__(self, hkdb=None, accnt=None, symbol=None, asset_info=None, uses_models=False):
        self.hkdb = hkdb
        self.accnt = accnt
        self.symbol = symbol
        self.asset_info = asset_info
        self.klines = None
        self.first_hourly_ts = 0
        self.last_update_ts = 0
        self.last_hourly_ts = 0
        self.last_ts = 0
        self.uses_models = uses_models

    def load(self, start_ts=0, end_ts=0, ts=0):
        pass

    def update(self, ts):
        pass
