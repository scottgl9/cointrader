from trader import OrderBookGDAX
from trader.account.AccountGDAX import AccountGDAX
from trader.indicator import QUAD, EMA, DiffWindow
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

class quadratic_with_fibonacci:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.strategy_name = 'quadratic_with_fibonacci'
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
        self.diffwindow = DiffWindow(30)
        self.last_price = 0.0

        # for fibonacci retraceement
        self.level1 = self.level2 = self.level3 = 0.0
        self.level0 = self.level4 = 0.0

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

    def update_fibonacci(self, price):
        diff = self.high_24hr - self.low_24hr
        self.level0 = self.low_24hr
        self.level1 = self.high_24hr - 0.236 * diff
        self.level2 = self.high_24hr - 0.382 * diff
        self.level3 = self.high_24hr - 0.618 * diff
        self.level4 = self.high_24hr

    def get_fibonacci_band(self, price):
        band = 0
        min_band = 0
        max_band = 0
        if price < self.level1:
            band = 1
            min_band = self.level0
            max_band = self.level1
        elif price >= self.level1 and price < self.level2:
            band = 2
            min_band = self.level1
            max_band = self.level2
        elif price >= self.level2 and price < self.level3:
            band = 3
            min_band = self.level2
            max_band = self.level3
        elif price >= self.level3:
            band = 4
            min_band = self.level3
            max_band = self.level4
        return [band, min_band, max_band]

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

        #band, minband, maxband = self.get_fibonacci_band(price)

        A, B, C = self.quad.compute()

        if C > 0.0 and C >= self.accnt.round_quote(self.accnt.low_24hr * 0.75) and C <= self.accnt.round_quote(self.accnt.high_24hr * 1.25):
            self.buy_signal_count += 1
            self.accnt.get_account_balance()
            size = self.accnt.round_base(self.accnt.quote_currency_available / price)

            buys_too_low = False
            for buy_price in self.order_handler.pending_buy_price_list:
                if price > 1.05 * buy_price:
                    buys_too_low = True
            if buys_too_low:
                #self.order_handler.cancel_buy_orders()
                #self.order_handler.cancel_sell_orders()
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()
            if C < price:
                buy_price = self.accnt.round_quote(C)
                if abs(buy_price - price) > self.accnt.min_market_funds:
                    self.order_handler.buy_limit(buy_price, self.accnt.base_min_size)
                self.accnt.get_account_balance()
        elif self.diffwindow.detect_valley():
            self.accnt.get_account_balance()
            buys_too_low = False
            for buy_price in self.order_handler.pending_buy_price_list:
                if price > 1.05 * buy_price:
                    buys_too_low = True
            if buys_too_low:
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()
            self.order_handler.buy_limit(price * 0.995, self.accnt.base_min_size)
            self.buy_signal_count += 1
            self.accnt.get_account_balance()

    def sell_signal(self, price):
        if self.accnt.funds_available < self.accnt.base_min_size:
            return

        #band, minband, maxband = self.get_fibonacci_band(price)
        A, B, C = self.quad.compute()

        if C > 0.0 and C >= self.accnt.round_quote(self.accnt.low_24hr * 0.75) and C <= self.accnt.round_quote(self.accnt.high_24hr * 1.25):
            self.sell_signal_count += 1
            self.accnt.get_account_balance()
            size = self.accnt.round_base(self.accnt.quote_currency_available / price)
            sells_too_low = False
            for sell_price in self.order_handler.pending_sell_price_list:
                if price < 0.95 * sell_price:
                    sells_too_low = True
            if sells_too_low:
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()
            if C > price:
                sell_price = self.accnt.round_quote(C)
                if abs(sell_price - price) > self.accnt.min_market_funds:
                    self.order_handler.sell_limit(sell_price, self.accnt.base_min_size)
                self.accnt.get_account_balance()
        elif self.diffwindow.detect_peak():
            self.accnt.get_account_balance()
            sells_too_low = False
            for sell_price in self.order_handler.pending_sell_price_list:
                if price < 0.95 * sell_price:
                    sells_too_low = True
            if sells_too_low:
                self.order_handler.cancel_all()
                self.accnt.get_account_balance()
            self.order_handler.sell_limit(price * 1.005, 0.01)
            self.sell_signal_count += 1
            self.accnt.get_account_balance()

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

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        price = float(msg["price"])
        self.update_last_50_prices(price)
        timestamp = 0 #datetime_to_float(aniso8601.parse_datetime(msg['time']))
        self.order_handler.update_market_price(price)
        self.update_fibonacci(price)
        self.order_handler.process_limit_orders(price)

        ts = self.quad.update(self.ema_quad.update(price))
        self.quad.compute()
        if ts != 0 and self.quad.A != 0.0 and self.quad.B != 0.0 and self.quad.C != 0.0:
            self.diffwindow.update(self.quad.A * ts ** 2 + self.quad.B * ts + self.quad.C)

        self.buy_signal(price)
        self.sell_signal(price)

        self.last_price = price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass
