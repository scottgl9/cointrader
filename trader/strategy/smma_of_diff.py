from trader import OrderBookGDAX
from trader.account.AccountGDAX import AccountGDAX
from trader import OrderHandler
from trader.indicator import SMMA, EMA
from trader.account import gdax


class smma_of_diff(object):
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
        else:
            self.order_handler = order_handler
        self.smma = SMMA(14)
        self.smma_diff = SMMA(14)
        self.ema = EMA(30)
        self.ema_last_price = self.smma_last_price = 0.0
        self.smma_last_diff_amount = self.smma_diff_amount = 0.0
        self.last_signal_price = 0.0
        self.buy_signal_count = self.sell_signal_count = 0
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

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def html_run_stats(self):
        results = str("<b>Strategy {} Stats:</b><br>".format(self.__class__.__name__))
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

    def buy_signal(self, price):
        if self.smma_diff_amount < self.smma_last_diff_amount:
            self.buy_signal_count += 1
            self.accnt.get_account_balance()
            size = self.accnt.quote_currency_balance / price
            #print("LT price: {} sma_diff_amount: {} last_diff_amount: {} size: {}".format(price, smma_diff_amount, self.smma_last_diff_amount, size))
            #if size >= 0.01:
            #    if self.accnt.buy_market(size):
            #        self.buy_price = price
            self.order_handler.buy_limit(price, 0.01)

    def sell_signal(self, price):
        if self.smma_diff_amount > self.smma_last_diff_amount:
            self.sell_signal_count += 1
            #print("GT price: {} sma_diff_amount: {} last_diff_amount: {} size: {}".format(price, smma_diff_amount, self.smma_last_diff_amount, self.accnt.funds_available))
            self.accnt.get_account_balance()
            #if self.accnt.funds_available >= 0.01:
            self.order_handler.sell_limit(price, 0.01)# self.accnt.funds_available)
            #    if self.buy_price != 0.0 and ((price - self.buy_price) / self.buy_price) > 0.005:
            #        self.accnt.sell_market(self.accnt.funds_available)

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
        self.order_handler.process_limit_orders(price)
        smma_price = float(self.smma.update(price))
        self.smma_diff_amount = float(self.smma_diff.update(smma_price - self.smma_last_price))
        ema_price = float(self.ema.update(price))

        self.buy_signal(price)
        self.sell_signal(price)

        self.smma_last_price = smma_price
        self.ema_last_price = ema_price
        self.smma_last_diff_amount = self.smma_diff_amount

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass