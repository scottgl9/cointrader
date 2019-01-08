class trade_size_strategy_base(object):
    def __init__(self, accnt, asset_info):
        self.accnt = accnt
        self.asset_info = asset_info
        self.base = asset_info.base
        self.currency = asset_info.currency
        self.symbol = self.accnt.make_ticker_id(self.base, self.currency)
        self.base_step_size = float(asset_info.base_step_size)
        self.currency_step_size = float(asset_info.currency_step_size)
        self.tickers = None

    def compute_trade_size(self, price):
        pass

    def check_buy_trade_size(self, size):
        pass

    def round_base(self, price):
        if self.base_step_size != 0.0:
            return round(price, '{:.9f}'.format(self.base_step_size).index('1') - 1)
        return price

    def round_quote(self, price):
        if self.currency_step_size != 0.0:
            return round(price, '{:.9f}'.format(self.currency_step_size).index('1') - 1)
        return price

    def my_float(self, value):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            return "{:.9f}".format(float(value))

    def update_tickers(self, tickers):
        self.tickers = tickers
