from trader.signal.SigType import SigType
from trader.signal.SignalBase import SignalBase


class BTC_USDT_Signal(SignalBase):
    def __init__(self):
        super(BTC_USDT_Signal, self).__init__()
        self.signal_name = "BTC_USDT_Signal"
        self.global_signal = True
        self.global_filter = "BTCUSDT"

    def pre_update(self, close, volume, ts):
        pass

    def post_update(self, close, volume):
        pass

    def sell_long_signal(self):
        return False

    def buy_signal(self):
        return False

    def sell_signal(self):
        return False
