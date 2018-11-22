class trade_size_strategy_base(object):
    def __init__(self, base, currency, base_min_size, tick_size, btc=0, eth=0, bnb=0, usdt=0):
        self.base = base
        self.currency = currency
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.tickers = None

    def compute_trade_size(self, price):
        pass

    def check_buy_trade_size(self, size):
        pass

    def round_base(self, price):
        if self.base_min_size != 0.0:
            return round(price, '{:.9f}'.format(self.base_min_size).index('1') - 1)
        return price

    def round_quote(self, price):
        if self.quote_increment != 0.0:
            return round(price, '{:.9f}'.format(self.quote_increment).index('1') - 1)
        return price

    def my_float(self, value):
        return str("{:.9f}".format(float(value)))

    def update_tickers(self, tickers):
        self.tickers = tickers
