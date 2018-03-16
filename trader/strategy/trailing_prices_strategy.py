from trader import OrderBookGDAX
from trader import AccountGDAX
from trader.indicator import MACD, QUAD, EMA, DiffWindow
from trader import OrderHandler
from trader import gdax
from trader.MeasureTrend import MeasureTrend
from datetime import timedelta, datetime
import aniso8601

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

class trailing_prices_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.strategy_name = 'trailing_prices_strategy'
        self.client = client
        if not account_handler:
            self.accnt = AccountGDAX(self.client, name, currency)
        else:
            self.accnt = account_handler
        self.products = [self.accnt.ticker_id]
        self.orderbook = OrderBookGDAX()
        #if not order_handler:
        self.order_handler = OrderHandler(self.accnt)
        self.trend = MeasureTrend()
        self.last_price = self.price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

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

    def buy_signal(self, price):
        # if we have insuffient funds to buy
        size = self.accnt.round_base(self.accnt.quote_currency_available / price)
        if size < self.accnt.base_min_size:
            return

        #if not self.trend.trending_downward():
        #    return

        # don't buy for greater than the price of the last sell
        if len(self.order_handler.pending_sell_price_list) != 0 and \
                price >= min(self.order_handler.pending_sell_price_list) - self.accnt.min_market_funds:
            return

        step = self.accnt.min_market_funds
        if self.accnt.currency == 'BTC':
            step = self.accnt.quote_increment

        buy_price = price - step
        if self.last_buy_price == 0.0 or abs(self.last_buy_price - buy_price) > step:
            self.order_handler.buy_limit(buy_price, self.accnt.base_min_size)
            self.last_buy_price = buy_price
            self.accnt.get_account_balance()

            #sell_price = price + self.accnt.min_market_funds * 3
            #self.order_handler.sell_limit(sell_price, self.accnt.base_min_size)
            #self.accnt.get_account_balance()

    def sell_signal(self, price):
        if self.accnt.funds_available < self.accnt.base_min_size:
            return

        #if not self.trend.trending_upward():
        #    return

        # don't sell for less than the price of the last buy
        if len(self.order_handler.pending_buy_price_list) != 0 and \
                price <= max(self.order_handler.pending_buy_price_list) + self.accnt.min_market_funds:
            return


        step = self.accnt.min_market_funds
        if self.accnt.currency == 'BTC':
            step = self.accnt.quote_increment
        sell_price = price + step

        if self.last_sell_price == 0.0 or abs(self.last_sell_price - sell_price) > step:
            self.order_handler.sell_limit(sell_price, self.accnt.base_min_size)
            self.last_sell_price = sell_price
            self.accnt.get_account_balance()

            #buy_price = price - self.accnt.min_market_funds * 3
            #self.order_handler.buy_limit(buy_price, self.accnt.base_min_size)
            #self.accnt.get_account_balance()

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def update_last_50_prices(self, price):
        #if price in self.last_50_prices:
        #    return
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        self.price = float(msg["price"])
        self.update_last_50_prices(self.price)
        self.trend.update_price(self.price)
        timestamp = 0 #datetime_to_float(aniso8601.parse_datetime(msg['time']))
        self.order_handler.update_market_price(self.price)
        self.order_handler.process_limit_orders(self.price)

        #if self.trend.peak_detected(): print("peak detected")
        #if self.trend.valley_detected(): print("valley detected")
        #if self.trend.trending_upward(): print("trending upward")
        #if self.trend.trending_downward(): print("trending downward")

        if self.price != 0.0 and self.last_price != 0.0:
            self.buy_signal(self.price)
            self.sell_signal(self.price)

        self.last_price = self.price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass
