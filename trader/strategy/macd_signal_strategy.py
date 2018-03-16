from trader import OrderBookGDAX
from trader import AccountGDAX
from trader.indicator import MACD, DiffWindow
from trader import OrderHandler
from trader import gdax


class macd_signal_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.client = client
        if not account_handler:
            self.accnt = AccountGDAX(self.client, name, currency)
        else:
            self.accnt = account_handler
        self.products = [self.accnt.ticker_id]
        self.orderbook = OrderBookGDAX()
        if not order_handler:
            self.order_handler = OrderHandler(self.accnt)
        self.macd_det = 0.0
        self.last_macd_det = 0.0
        self.last_price = 0.0
        self.macd = MACD()
        self.diffwindow = DiffWindow(30)
        self.buy_signal_count = self.sell_signal_count = 0
        self.pc = gdax.PublicClient()

        # for fibonacci retraceement
        self.level1 = self.level2 = self.level3 = 0.0
        self.level0 = self.level4 = 0.0

        self.all_time_high = 0.0
        self.all_time_low = 0.0
        self.high_24hr = self.low_24hr = 0.0
        self.high_24hr_timestamp = 0
        self.low_24hr_timestamp = 0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.last_high_24hr_ts = 0.0
        self.last_low_24hr_ts = 0.0
        self.buy_price = 0.0
        self.last_50_prices = []
        #self.update_24hr_stats()
        print("Started {} strategy".format(self.__class__.__name__))

    def get_ticker_id(self):
        return self.accnt.ticker_id

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def html_run_stats(self):
        results = str('')
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

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

    def buy_signal(self, price):
        #if price > 0.95 * self.all_time_high:
        #    return

        if self.diffwindow.detect_valley():
            self.accnt.get_account_balance()
            size = round(self.accnt.quote_currency_available / price, 4)
            if size < 0.01:
                buys_too_low = False
                for buy_price in self.order_handler.pending_buy_price_list:
                    if price > 1.05 * buy_price:
                        buys_too_low = True
                if buys_too_low:
                    self.order_handler.cancel_buy_orders()
                    #self.order_handler.cancel_sell_orders()
                    self.accnt.get_account_balance()
            self.order_handler.buy_limit(price * 0.995, 0.01)
            self.buy_signal_count += 1

    def sell_signal(self, price):
        #if price < 1.05 * self.all_time_low:
        #    return

        if self.diffwindow.detect_peak():
            if self.accnt.funds_available < 0.01:
                sells_too_low = False
                for sell_price in self.order_handler.pending_sell_price_list:
                    if price < 0.95 * sell_price:
                        sells_too_low = True
                if sells_too_low:
                    self.order_handler.cancel_buy_orders()
                    self.order_handler.cancel_sell_orders()
                    self.accnt.get_account_balance()
            self.order_handler.sell_limit(price * 1.005, 0.01)
            self.sell_signal_count += 1

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        price = float(msg["price"])
        #timestamp = float(msg['timestamp'])
        self.update_last_50_prices(price)
        self.update_fibonacci(price)
        self.order_handler.update_market_price(price)
        self.order_handler.process_limit_orders(price)

        self.macd.update(price)
        self.macd_det = self.macd.result
        if self.macd_det != self.last_macd_det:
            self.diffwindow.update(self.macd_det)

        if self.all_time_high == 0.0 or self.all_time_low == 0.0:
            self.all_time_high = price
            self.all_time_low = price
        elif price > self.all_time_high:
            self.all_time_high = price
        elif price < self.all_time_low:
            self.all_time_low = price

        self.buy_signal(price)
        self.sell_signal(price)

        self.last_price = price
        self.last_macd_det = self.macd_det

        if self.last_low_24hr == 0 or self.last_high_24hr == 0:
            self.last_low_24hr = self.low_24hr
            self.last_high_24hr = self.high_24hr
            self.last_high_24hr_ts = self.high_24hr_timestamp
            self.last_low_24hr_ts = self.low_24hr_timestamp
        elif (self.high_24hr_timestamp - self.last_high_24hr_ts) > (3600.0 * 24.0):
            self.last_high_24hr = self.high_24hr
            self.last_high_24hr_ts = self.high_24hr_timestamp
        elif (self.low_24hr_timestamp - self.last_low_24hr_ts) > (3600.0 * 24.0):
            self.last_low_24hr = self.low_24hr
            self.last_low_24hr_ts = self.low_24hr_timestamp

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass