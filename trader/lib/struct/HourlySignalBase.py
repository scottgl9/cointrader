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

    def update(self, ts, last_hourly_ts=0):
        pass

    # enable / disable buy orders for live market signals
    def buy_enable(self):
        return True

    # enable/disable sell orders for live market signals
    def sell_enable(self):
        return True

    # buy signal which works the same as buy_signal() with live market signals
    def buy_signal(self):
        return False

    # sell long signal which works the same as sell_long_signal() with live market signals
    def sell_long_signal(self):
        return False

    # sell signal which works the same as sell_signal() with live market signals
    def sell_signal(self):
        return False
