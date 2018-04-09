# class to handle individual trade pair (ex. BTC/USD)
class TradePair(object):
    def __init__(self, client, accnt, strategy, base='BTC', currency='USD'):
        self.client = client
        self.accnt = accnt
        self.strategy = strategy
        #self.order_handler = order_handler
        self.base_name = base
        self.currency = currency
        self.ticker_id = self.accnt.make_ticker_id(base, currency)
        #print(self.accnt.get_fills(ticker_id=self.ticker_id))

        self.low_24hr = self.high_24hr = 0.0
        self.open_24hr = self.close_24hr = 0.0
        self.last_24hr = 0.0
        self.volume_24hr = 0.0
        self.quote_increment = 0.01
        self.base_min_size = 0.0
        self.market_price = 0.0
        #self.get_24hr_stats()
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.count_prices_added = 0

    def get_24hr_stats(self):
        stats = self.accnt.get_24hr_stats()
        self.low_24hr = stats['l']
        self.high_24hr = stats['h']
        self.open_24hr = stats['o']
        self.last_24hr = stats['c']
        self.volume_24hr = stats['v']

    def html_run_stats(self):
        return self.strategy.html_run_stats()

    def get_ticker_id(self):
        return self.ticker_id

    def buy_market(self, size):
        return self.accnt.buy_market(ticker_id=self.ticker_id, size=size)

    def sell_market(self, size):
        return self.accnt.sell_market(ticker_id=self.ticker_id, size=size)

    def get_klines(self, days=0, hours=1, ticker_id=None):
        return self.accnt.get_klines(days, hours, ticker_id)

    def set_market_price(self, price):
        self.market_price = price

    def run_update(self, msg):
        result = self.strategy.run_update(msg)
        self.last_50_prices = self.strategy.last_50_prices
        self.prev_last_50_prices = self.strategy.prev_last_50_prices
        self.count_prices_added = self.strategy.count_prices_added
        return result

    def clear_price_counter(self):
        self.strategy.count_prices_added = 0
        self.count_prices_added = 0

    def run_update_price(self, price):
        #if self.base_name == 'QTUM' and float(price) == 10.0: return
        #print("run_update_price({}, {}, {}".format(self.base_name, self.currency, price))
        return self.strategy.run_update_price(price)
