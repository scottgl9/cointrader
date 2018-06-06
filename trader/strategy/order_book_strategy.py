from trader import OrderBookGDAX
from trader.account.AccountGDAX import AccountGDAX
from trader.indicator import QUAD, EMA
from trader import OrderHandler
from trader.account import gdax
from datetime import datetime


# STRATEGY
# - if price is near the bottom of the band, and MACD trending downward, set buy limit order slightly above price
# - if price is near the top of the band, and MACD trending upward, set sell limit order slightly below price

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

class order_book_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.strategy_name = 'order_book_strategy'
        self.client = client
        if not account_handler:
            self.accnt = AccountGDAX(self.client, name, currency)
        else:
            self.accnt = account_handler
        self.products = [self.accnt.ticker_id]
        self.orderbook = OrderBookGDAX()
        #if not order_handler:
        self.order_handler = OrderHandler(self.accnt)
        self.quad = QUAD(30)
        self.ema_quad = EMA(9)
        self.last_price = self.price = 0.0

        self.watch_sell = False
        self.watch_buy = False
        self.pc = gdax.PublicClient()

        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.accnt.get_account_balance()
        self.update_24hr_stats()
        print("Started {} strategy".format(self.__class__.__name__))
        print("Account balance: {} USD - {} BTC".format(self.accnt.quote_currency_balance, self.accnt.balance))

    def get_ticker_id(self):
        return self.accnt.ticker_id

    def html_run_stats(self):
        results = str('')
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def buy_signal(self, price):
        # if we have insuffient funds to buy
        size = self.accnt.round_base(self.accnt.quote_currency_available / price)
        if size < self.accnt.base_min_size:
            return

        self.price_start, self.price_end, self.weight, self.resistance, \
        self.oprice, self.oweight = self.orderbook.compute_expected_price_movement(self.price)

        if self.price_start == 0.0 or self.price_end == 0.0:
            return

        if self.price_end <= (self.price_start - self.accnt.min_market_funds / 2.0) and self.weight > 5.0 and self.weight > (2.0 * self.resistance):
            buys_too_low = False
            for buy_price in self.order_handler.pending_buy_price_list:
                if price < 0.95 * buy_price:
                    buys_too_low = True
            if buys_too_low:
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()

            price = self.price_start - self.accnt.min_market_funds / 2.0
            while price >= self.price_end:
                self.order_handler.buy_limit(price, self.accnt.base_min_size)
                self.buy_signal_count += 1
                self.accnt.get_account_balance()
                price -= self.accnt.min_market_funds / 2.0

    def sell_signal(self, price):
        if self.accnt.funds_available < self.accnt.base_min_size:
            return

        self.price_start, self.price_end, self.weight, self.resistance, \
        self.oprice, self.oweight = self.orderbook.compute_expected_price_movement(self.price)

        if self.price_start == 0.0 or self.price_end == 0.0:
            return

        if self.price_end >= (self.price_start + self.accnt.min_market_funds / 2.0) and self.weight > 5.0 and self.weight > (2.0 * self.resistance):
            sells_too_low = False
            for sell_price in self.order_handler.pending_sell_price_list:
                if price > 1.05 * sell_price:
                    sells_too_low = True
            if sells_too_low:
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()

            price = self.price_start + self.accnt.min_market_funds / 2.0
            while price <= self.price_end:
                self.order_handler.sell_limit(price, self.accnt.base_min_size)
                self.sell_signal_count += 1
                self.accnt.get_account_balance()
                price += self.accnt.min_market_funds / 2.0

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        self.price = float(msg["price"])
        self.update_last_50_prices(self.price)
        timestamp = 0 #datetime_to_float(aniso8601.parse_datetime(msg['time']))
        self.order_handler.update_market_price(self.price)
        self.order_handler.process_limit_orders(self.price)

        if self.price != 0.0:
            self.buy_signal(self.price)
            self.sell_signal(self.price)

        self.last_price = self.price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)
        if self.price != 0.0:
            #print(msg)
            self.buy_signal(self.price)
            self.sell_signal(self.price)

    def close(self):
        pass
