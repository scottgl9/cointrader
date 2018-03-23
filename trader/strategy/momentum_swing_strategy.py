from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax
from trader.MeasureTrend import MeasureTrend
from trader.indicator.QUAD import QUAD
from trader.indicator.EMA import EMA
from datetime import datetime


def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

class momentum_swing_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0):
        self.strategy_name = 'trailing_prices_strategy'
        self.client = client
        # if not account_handler:
        #     self.accnt = AccountGDAX(self.client, name, currency)
        # else:
        self.accnt = account_handler
        #self.orderbook = OrderBookGDAX()
        #if not order_handler:
        #self.order_handler = OrderHandler(self.accnt)
        self.trend = MeasureTrend(window=50)
        self.quad = QUAD(30)
        self.ema_quad = EMA(9)
        self.last_price = self.price = 0.0

        self.base = name
        self.currency = currency

        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.trend_upward_count = 0
        self.trend_downward_count = 0
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.buy_price_list = []
        self.ticker_id = self.accnt.make_ticker_id(name, currency)

    def get_ticker_id(self):
        return self.ticker_id

    def html_run_stats(self):
        results = str('')
        results += "buy_signal_count: {}<br>".format(self.buy_signal_count)
        results += "sell_signal_count: {}<br>".format(self.sell_signal_count)
        return results

    def get_lowest_buy_price(self, order_price):
        if len(self.buy_price_list) == 0: return 0.0
        lowest_price = float(self.buy_price_list[0])
        for i in range(1, len(self.buy_price_list)):
            if float(order_price) > float(self.buy_price_list[i]):
                lowest_price = self.buy_price_list[i]

        # sell for at least one tick up from minimum buy price
        if order_price <= lowest_price: # + self.accnt.quote_increment):
            #self.limit_sell_order_price_too_low += 1
            return 0.0
        return lowest_price

    def round_base(self, price):
        return round(price, '{:f}'.format(self.base_min_size).index('1') - 1)

    def round_quote(self, price):
        return round(price, '{:f}'.format(self.quote_increment).index('1') - 1)

    def buy_signal(self, price):
        for order_price in self.buy_price_list:
            if order_price - self.quote_increment <= price <= order_price + self.quote_increment:
                return

        if self.last_sell_price != 0.0 and price >= self.last_sell_price:
            return

        buy_flag = False
        if self.trend.valley_detected():
            #print("{}{} valley detected".format(self.base, self.currency))
            if self.trend_downward_count > 3:
                buy_flag = True
            self.trend_upward_count = 0
            self.trend_downward_count = 0
            #print("buy({}, {})".format(self.base, self.currency))
        if self.trend.trending_upward():
            if self.trend_upward_count > 3:
                buy_flag = True
            #print("{}{} trending upward".format(self.base, self.currency))
            self.trend_downward_count = 0
            self.trend_upward_count += 1

        # if we have insuffient funds to buy
        #size = self.accnt.round_base(self.accnt.quote_currency_available / price)
        balance_available = self.accnt.get_asset_balance(self.currency)['available']
        size = self.round_base(float(balance_available) / float(price))

        if size < self.base_min_size:
            return

        #print("buy_signal({})".format(price))
        #if buy_flag:
        if self.last_buy_price != 0.0 and self.last_sell_price != 0.0:
            print("buy({}{}, {}) @ {}".format(self.base, self.currency, self.base_min_size, price))
            self.buy_price_list.append(price)
            print(self.accnt.buy_market(self.base_min_size, ticker_id=self.get_ticker_id()))
        self.last_buy_price = price
        self.accnt.get_account_balances()

    def sell_signal(self, price):
        if len(self.buy_price_list) == 0.0: return

        if self.last_buy_price != 0.0 and price <= self.last_buy_price:
            return

        sell_flag = False
        if self.trend.peak_detected():
            #print("{}{} peak detected".format(self.base, self.currency))
            #if self.trend_upward_count > 2:
            sell_flag = True
            self.trend_upward_count = 0
            self.trend_downward_count = 0
            #print("sell({}, {})".format(self.base, self.currency))
        if self.trend.trending_downward():
            #if self.trend_downward_count > 2:
            sell_flag = True
            #print("{}{} trending downward".format(self.base, self.currency))
            self.trend_upward_count = 0
            self.trend_downward_count += 1
        else:
            buy_price = self.get_lowest_buy_price(price)
            if buy_price != 0.0 and (price - buy_price) / buy_price > 0.01:
                sell_flag = True

        balance_available = self.round_base(float(self.accnt.get_asset_balance(self.base)['available']))
        #if balance_available != 0.0:
        #    print("{} = {}, {}".format(self.base, balance_available, self.base_min_size))
        if balance_available < self.base_min_size:
            #if self.accnt.get_asset_balance(self.base) > 0.0:
            #    print(self.accnt.get_asset_balance(self.base), self.base_min_size)
            return

        #if sell_flag:
        buy_price = self.get_lowest_buy_price(price)
        if buy_price == 0.0: return
        if (price - buy_price) / buy_price < 0.001: return

        if self.last_buy_price != 0.0 and self.last_sell_price != 0.0:
            print("sell({}{}, {}) @ {}".format(self.base, self.currency, self.base_min_size, price))
            print(self.accnt.sell_market(self.base_min_size, ticker_id=self.get_ticker_id()))
            self.buy_price_list.remove(buy_price)

        self.last_sell_price = price

        self.accnt.get_account_balances()

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
        ts = self.quad.update(self.ema_quad.update(price))
        self.quad.compute()
        if ts != 0 and self.quad.A != 0.0 and self.quad.B != 0.0 and self.quad.C != 0.0 \
            and abs((self.quad.C - price) / self.quad.C) < 0.001:

            #print(self.ticker_id, self.quad.C)
            if self.quad.C < price and self.trend.sma_prices[0] > self.trend.sma_prices[-1]:
                print("{} Valley at {}".format(self.ticker_id, self.quad.C))
                self.buy_signal(price)
            elif self.quad.C > price and self.trend.sma_prices[0] < self.trend.sma_prices[-1]:
                print("{} Peak at {}".format(self.ticker_id, self.quad.C))
                self.sell_signal(price)
        timestamp = 0 #datetime_to_float(aniso8601.parse_datetime(msg['time']))
        #self.order_handler.update_market_price(self.price)

        self.last_price = price

    def run_update_orderbook(self, msg):
        pass
    #    self.orderbook.process_update(msg)

    def close(self):
        pass
