from trader.lib.struct.SigType import SigType

class SignalBase(object):
    FLAG_SELL_BOUGHT = 1
    FLAG_SELL_ALL = 2

    def __init__(self, accnt=None, symbol=None, asset_info=None):
        self.id = 0
        self.asset_info = asset_info
        self.symbol = symbol
        self.flag = self.FLAG_SELL_BOUGHT
        self.buy_type = SigType.SIGNAL_NONE
        self.sell_type = SigType.SIGNAL_NONE
        self.mm_enabled = False
        self.cache = None
        self.accnt = accnt
        self.base = None
        self.currency = None
        if self.asset_info:
            self.base = self.asset_info.base
            self.currency = self.asset_info.currency

        self.is_currency_pair = False
        if self.asset_info and self.asset_info.is_currency_pair:
            self.is_currency_pair = True

        # settings for global signals
        self.global_signal = False
        self.global_filter = "*"

        self.max_tpprofit = 0
        self.tpprofit = 0
        self.last_tpprofit = 0
        self.timestamp = 0
        self.last_timestamp = 0
        self.multi_order_tracker = None
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

        # define buy type and sell type to help with determining which condition in signal
        # initiated the buy or sell (0 = NONE, 1=TYPE1, 2=TYPE2, etc)
        self.buy_type = 0
        self.sell_type = 0

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

    def pre_update(self, close, volume, ts, cache_db=None):
        pass

    def post_update(self, close, volume):
        pass

    def sell_long_signal(self):
        return False

    def buy_signal(self):
        return False

    def sell_signal(self):
        return False

    def set_total_percent_profit(self, tpprofit):
        if tpprofit != 0 and tpprofit == self.last_tpprofit:
            return
        if tpprofit > self.max_tpprofit:
            self.max_tpprofit = tpprofit
        self.last_tpprofit = self.tpprofit
        self.tpprofit = tpprofit
