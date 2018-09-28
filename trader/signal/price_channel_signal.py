from trader.indicator.test.PriceChannel import PriceChannel


class price_channel_signal(object):
    def __init__(self, window=26):
        self.signal_name = "price_channel_signal"
        self.id = 0
        self.window = window
        #self.obv = OBV()
        self.pc = PriceChannel()

        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_timestamp = 0
        self.buy_order_id = None
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

    def set_id(self, id):
        self.id = id

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
