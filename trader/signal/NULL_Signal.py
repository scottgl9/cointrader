from trader.lib.struct.SignalBase import SignalBase


class NULL_Signal(SignalBase):
    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None):
        super(NULL_Signal, self).__init__(accnt, symbol, asset_info, kdb)
        self.signal_name = "NULL_Signal"

    def pre_update(self, close, volume, ts):
        pass

    def buy_signal(self):
        return False

    def sell_long_signal(self):
        return False

    def sell_signal(self):
        return False
