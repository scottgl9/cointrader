from trader.signal.SigType import SigType

class SignalBase(object):
    def __init__(self):
        self.id = 0
        self.buy_type = SigType.SIGNAL_NONE
        self.sell_type = SigType.SIGNAL_NONE

        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_timestamp = 0
        self.buy_order_id = None
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

    def set_id(self, id):
        self.id = id

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
