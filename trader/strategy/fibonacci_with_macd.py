from trader import OrderBookGDAX
from trader import AccountGDAX
from trader.indicator import MACD
from trader import OrderHandler
from trader.account import gdax


# STRATEGY
# - if price is near the bottom of the band, and MACD trending downward, set buy limit order slightly above price
# - if price is near the top of the band, and MACD trending upward, set sell limit order slightly below price

class fibonacci_with_macd:
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
        self.macd = MACD()
        self.last_macd_diff = 0.0
        self.last_macd_signal = 0.0
        self.last_macd_det = 0.0
        self.macd_det = 0.0
        self.macd_det_diff = 0.0
        self.last_macd_det_diff = 0.0
        self.last_price = 0.0
        self.buy_signal_count = self.sell_signal_count = 0

        # for fibonacci retraceement
        self.level1 = self.level2 = self.level3 = 0.0
        self.level0 = self.level4 = 0.0

        self.watch_sell = False
        self.watch_buy = False
        self.pc = gdax.PublicClient()

        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.buy_price = 0.0
        self.last_50_prices = []
        #self.update_24hr_stats()
        print("Started {} strategy".format(self.__class__.__name__))

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
        band, minband, maxband = self.get_fibonacci_band(price)

        if price < (minband + 0.1 * (maxband - minband)) and price > minband: # and self.macd_det > self.last_macd_det:
            self.buy_signal_count += 1
            #print("buy_signal({}, {}, {}".format(band, minband, maxband))
            self.accnt.get_account_balance()
            size = round(self.accnt.quote_currency_available / (price * 1.03), 4)
            if size >= 0.01 and self.buy_price == 0.0:  # and price < (self.high_24hr + 2*self.low_24hr) / 3.0:
                self.order_handler.buy_market(minband * 1.03, size)
                self.buy_price = price
                return True
        elif price > (minband + 0.1 * (maxband - minband)) and price < (maxband - 0.1 * (maxband - minband)):
            self.buy_signal_count += 1
            self.accnt.get_account_balance()
            if self.accnt.funds_available >= 0.01 and self.buy_price != 0.0 and price > self.buy_price:  # and self.accnt.buy_price != 0.0:
                self.order_handler.sell_market(maxband * 0.997, self.accnt.funds_available)
                self.buy_price = 0.0
                return True
            return False

    def sell_signal(self, price):
        band, minband, maxband = self.get_fibonacci_band(price)
        if price > (maxband - 0.1 * (maxband - minband)) and price < maxband: # and self.macd_det < self.macd_det_diff:
            self.sell_signal_count += 1
            #print("sell_signal({}, {}, {}".format(band, minband, maxband))
            self.accnt.get_account_balance()
            if self.accnt.funds_available >= 0.01 and self.buy_price != 0.0 and price > self.buy_price: # and self.accnt.buy_price != 0.0:
                self.order_handler.sell_market(maxband * 0.997, self.accnt.funds_available)
                self.buy_price = 0.0
                return True
        elif price > (minband + 0.2 * (maxband - minband)) and price < (maxband - 0.1 * (maxband - minband)):
            self.sell_signal_count += 1
            self.accnt.get_account_balance()
            if self.accnt.funds_available >= 0.01 and self.buy_price != 0.0 and price > self.buy_price: # and self.accnt.buy_price != 0.0:
                self.order_handler.sell_market(maxband * 0.997, self.accnt.funds_available)
                self.buy_price = 0.0
                return True
            return False

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
        self.order_handler.update_market_price(price)
        self.update_fibonacci(price)
        #self.order_handler.process_limit_orders(price)

        self.macd.update(price)
        macd_diff = self.macd.diff
        macd_signal = self.macd.signal.result
        self.macd_det = self.macd.result

        self.buy_signal(price)
        self.sell_signal(price)

        self.last_macd_diff = macd_diff
        self.last_macd_signal = macd_signal
        if self.macd_det != 0.0:
            self.last_macd_det = self.macd_det
        if self.macd_det_diff != 0.0:
            self.last_macd_det_diff = self.macd_det_diff
            self.last_price = price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass