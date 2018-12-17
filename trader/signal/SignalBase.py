from trader.signal.SigType import SigType

class SignalBase(object):
    FLAG_SELL_BOUGHT = 1
    FLAG_SELL_ALL = 2

    def __init__(self, accnt=None):
        self.id = 0
        self.symbol = None
        self.flag = self.FLAG_SELL_BOUGHT
        self.buy_type = SigType.SIGNAL_NONE
        self.sell_type = SigType.SIGNAL_NONE
        self.mm_enabled = False
        self.cache = None
        self.accnt = accnt

        # settings for global signals
        self.global_signal = False
        self.global_filter = "*"

        self.timestamp = 0
        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_timestamp = 0
        self.sell_timestamp = 0
        self.buy_order_id = None
        self.last_buy_price = 0.0
        self.last_buy_ts = 0
        self.last_sell_price = 0.0
        self.last_sell_ts = 0
        # highest close price encountered after bought, to determine if there
        # is no upward movement
        self.buy_price_high = 0.0

        # for limit / stop loss orders
        self.buy_pending = False
        self.buy_pending_price = 0.0
        self.sell_pending = False
        self.sell_pending_price = 0.0
        self.sell_marked = False

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def is_global(self):
        return self.global_signal

    def get_symbol(self):
        return self.symbol

    def set_symbol(self, symbol):
        self.symbol = symbol

    def get_flag(self):
        return self.flag

    def set_flag(self, flag):
        self.flag = flag

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
