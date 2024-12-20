from trader.lib.struct.SigType import SigType

class SignalBase(object):
    # realtime signal
    TYPE_SIGNAL_RT = 1
    # hourly signal
    TYPE_SIGNAL_HR = 2
    # realtime and hourly signal
    TYPE_SIGNAL_RT_HR = 3

    def __init__(self, accnt=None, symbol=None, asset_info=None, kdb=None, type=TYPE_SIGNAL_RT, uses_models=False):
        self.id = 0
        self.asset_info = asset_info
        self.symbol = symbol
        self.kdb = kdb
        self.type = type
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
        self.last_start_sell_ts = 0
        self.buy_price_high = 0.0

        # hourly variables
        self.uses_models = uses_models
        self.klines = None
        self.first_hourly_ts = 0
        self.last_update_ts = 0
        self.last_hourly_ts = 0

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

    # realtime pre update
    def pre_update(kline):
        pass

    # realtime post update
    def post_update(kline):
        pass

    # realtime sell long signal
    def sell_long_signal(self):
        return False

    # realtime buy signal
    def buy_signal(self):
        return False

    # realtime sell signal
    def sell_signal(self):
        return False

    # hourly load
    def hourly_load(self, hourly_ts=0, pre_load_hours=0, ts=0):
        pass

    # hourly update
    def hourly_update(self, hourly_ts):
        pass

    # hourly enable / disable buy orders for live market signals
    def hourly_buy_enable(self):
        return True

    # enable/disable sell orders for live market signals
    def hourly_sell_enable(self):
        return True

    def hourly_mode_update(self, kline):
        pass

    # hourly buy signal
    def hourly_buy_signal(self):
        return False

    # hourly sell long signal
    def hourly_sell_long_signal(self):
        return False

    # hourly sell signal
    def hourly_sell_signal(self):
        return False

    def set_total_percent_profit(self, tpprofit):
        if tpprofit != 0 and tpprofit == self.last_tpprofit:
            return
        if tpprofit > self.max_tpprofit:
            self.max_tpprofit = tpprofit
        self.last_tpprofit = self.tpprofit
        self.tpprofit = tpprofit
