from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax
from trader.MeasureTrend import MeasureTrend
from trader.indicator.QUAD import QUAD
from trader.indicator.EMA import EMA
from trader.indicator.MACD import MACD
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)


class macd_quad_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0):
        self.strategy_name = 'macd_quad_strategy'
        self.client = client
        # if not account_handler:
        #     self.accnt = AccountGDAX(self.client, name, currency)
        # else:
        self.accnt = account_handler
        self.ticker_id = self.accnt.make_ticker_id(name, currency)
        self.last_price = self.price = 0.0
        self.macd = MACD(12.0*24.0, 26.0*24.0, 9.0*24.0)
        self.quad = QUAD()
        self.trend = MeasureTrend(name=self.ticker_id, window=50)

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
        #self.accnt.get_account_balances()

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
        if self.quad.C <= 0.0 or self.quad.C > self.macd.diff or self.trend.trending_downward():
            return

        if not self.trend.trending_upward():
            return

        if self.trend_upward_count < 5: return
        #print("buy_signal({}, {})".format(self.ticker_id, price))

        for order_price in self.buy_price_list:
            if order_price - (self.quote_increment * 4) <= price <= order_price + (self.quote_increment * 4):
                continue

        if self.last_sell_price != 0.0 and price >= self.last_sell_price:
            return

        # if we have insuffient funds to buy
        balance_available = self.accnt.get_asset_balance(self.currency)['available']
        size = self.round_base(float(balance_available) / float(price))

        if size < self.base_min_size:
            return

        # for now limit to no more than 4 buys at any one time
        if len(self.buy_price_list) > 3:
            return


        result = self.accnt.buy_market(float(self.base_min_size), ticker_id=self.get_ticker_id())
        if 'status' in result and result['status'] == 'FILLED':
            print("buy({}{}, {}) @ {}".format(self.base, self.currency, self.base_min_size, price))
            self.buy_price_list.append(price)
            self.last_buy_price = price
        self.accnt.get_account_balances()

    def sell_signal(self, price):
        if self.quad.C < self.macd.diff or self.trend.trending_upward():
            return

        #print("sell_signal({}, {})".format(self.ticker_id, price))

        if len(self.buy_price_list) == 0: return

        #if self.trend_downward_count < 2: return

        if self.last_buy_price != 0.0 and price <= self.last_buy_price:
            return

        buy_price = self.get_lowest_buy_price(price)
        if buy_price == 0.0 or (price - buy_price) / buy_price < 0.01:
            return

        balance_available = self.round_base(float(self.accnt.get_asset_balance(self.base)['available']))
        if balance_available < self.base_min_size:
            return

        result = self.accnt.sell_market(float(self.base_min_size), ticker_id=self.get_ticker_id())
        if 'status' in result and result['status'] == 'FILLED':
            print("sell({}{}, {}) @ {}".format(self.base, self.currency, self.base_min_size, price))
            self.buy_price_list.remove(buy_price)
            self.last_sell_price = price
            total_usd, total_btc = self.accnt.get_account_total_value()
            print("Total balance USD = {}, BTC={}".format(total_usd, total_btc))
        self.accnt.get_account_balances()

    def update_last_50_prices(self, price):
        #if price in self.last_50_prices:
        #    return
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, price):
        self.macd.update(price)
        self.quad.update(self.macd.diff)
        self.quad.compute()
        self.trend.update_price(self.macd.diff)
        if self.trend.trending_upward():
            self.trend_upward_count += 1
            self.trend_downward_count = 0
        elif self.trend.trending_downward():
            self.trend_upward_count = 0
            self.trend_downward_count += 1

        self.buy_signal(price)
        self.sell_signal(price)

    def run_update_orderbook(self, msg):
        pass
    #    self.orderbook.process_update(msg)

    def close(self):
        logger.info("close()")
        pass
