from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax
from trader.MeasureTrend import MeasureTrend
from datetime import datetime


def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

class momentum_swing_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.strategy_name = 'trailing_prices_strategy'
        self.client = client
        # if not account_handler:
        #     self.accnt = AccountGDAX(self.client, name, currency)
        # else:
        self.accnt = account_handler
        self.products = [self.accnt.ticker_id]
        self.orderbook = OrderBookGDAX()
        #if not order_handler:
        #self.order_handler = OrderHandler(self.accnt)
        self.trend = MeasureTrend(window=50)
        self.last_price = self.price = 0.0

        self.base = name
        self.currency = currency

        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        #self.accnt.get_account_balance()
        #self.update_24hr_stats()
        #print("Started {} strategy".format(self.__class__.__name__))
        #print("Account balance: {} USD - {} BTC".format(self.accnt.quote_currency_balance, self.accnt.balance))

    def get_ticker_id(self):
        return self.accnt.ticker_id

    def html_run_stats(self):
        results = str('')
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

    def buy_signal(self, price):
        # if we have insuffient funds to buy
        size = self.accnt.round_base(self.accnt.quote_currency_available / price)
        if size < self.accnt.base_min_size:
            return

    def sell_signal(self, price):
        if self.accnt.funds_available < self.accnt.base_min_size:
            return

    def update_last_50_prices(self, price):
        #if price in self.last_50_prices:
        #    return
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, price):
        #if 'type' in msg and 'match' not in msg['type']: return

        #elf.price = float(msg["price"])
        self.update_last_50_prices(price)
        self.trend.update_price(price)
        timestamp = 0 #datetime_to_float(aniso8601.parse_datetime(msg['time']))
        #self.order_handler.update_market_price(self.price)

        if self.trend.peak_detected(): print("{}{} peak detected".format(self.base, self.currency))
        if self.trend.valley_detected(): print("{}{} valley detected".format(self.base, self.currency))
        if self.trend.trending_upward(): print("{}{} trending upward".format(self.base, self.currency))
        if self.trend.trending_downward(): print("{}{} trending downward".format(self.base, self.currency))

        #if price != 0.0 and self.last_price != 0.0:
        #    self.buy_signal(price)
        #    self.sell_signal(price)

        self.last_price = price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass
