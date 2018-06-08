from trader.indicator.test.PriceChannel import PriceChannel


class price_channel_signal(object):
    def __init__(self, window=26):
        self.window = window
        #self.obv = OBV()
        self.pc = PriceChannel()

    def pre_update(self, close, volume, ts):
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
