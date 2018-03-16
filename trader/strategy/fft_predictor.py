from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax


class fft_predictor:
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

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        price = float(msg["price"])
        self.update_last_50_prices(price)
        self.order_handler.update_market_price(price)

        #self.buy_signal(price)
        #self.sell_signal(price)
        self.last_price = price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass