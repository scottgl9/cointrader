from trader.lib.struct.SignalBase import SignalBase


class NULL_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, hkdb=None):
        super(NULL_Signal, self).__init__(accnt, symbol, asset_info, hkdb)
        self.signal_name = "NULL_Signal"

    def pre_update(self, close, volume, ts, cache_db=None):
        pass

    def buy_signal(self):
        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        return False