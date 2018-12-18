from trader.indicator.test.PriceChannel import PriceChannel
from trader.signal.SignalBase import SignalBase

class price_channel_signal(SignalBase):
    def __init__(self, accnt=None, window=26):
        super(price_channel_signal, self).__init__(accnt)
        self.signal_name = "price_channel_signal"
        self.id = 0
        self.window = window
        #self.obv = OBV()
        self.pc = PriceChannel()

    def pre_update(self, close, volume, ts, cache_db=None):
        self.pc.update(close)

    def post_update(self, close, volume):
        pass

    def buy_signal(self):
        if self.pc.split_up():
            return True
        return False

    def sell_signal(self):
        if self.pc.split_down():
            return True
        return False
