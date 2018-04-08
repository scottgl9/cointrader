from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax
from trader.MeasureTrend import MeasureTrend
from trader.indicator.QUAD import QUAD
from trader.indicator.EMA import EMA
from trader.indicator.RSI import RSI
from trader.indicator.MACD import MACD
from trader.indicator.ROC import ROC
from trader.indicator.TSI import TSI
from trader.Crossover import Crossover
from datetime import datetime
#import logging

#logger = logging.getLogger(__name__)

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)


class momentum_swing_strategy:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0):
        self.strategy_name = 'momentum_swing_strategy'
        self.client = client
        self.accnt = account_handler
        self.ticker_id = self.accnt.make_ticker_id(name, currency)
        self.last_price = self.price = 0.0
        self.macd = MACD(12.0*24.0, 26.0*24.0, 9.0*24.0)
        self.quad = QUAD()
        self.rsi = RSI()
        self.rsi_result = 0.0
        self.last_rsi_result = 0.0
        self.roc = ROC()
        self.macd_trend = MeasureTrend(name=self.ticker_id, window=50)
        self.price_trend = MeasureTrend(name=self.ticker_id, window=50)
        self.tsi = TSI()
        self.last_tsi_result = 0.0
        self.cross_short = Crossover()
        self.cross_long = Crossover()
        self.ema12 = EMA(12, scale=24)
        self.ema26 = EMA(26, scale=24)
        self.ema50 = EMA(50, scale=24)
        self.ema100 = EMA(100)
        self.ema_volume = EMA(12)
        #self.trend_tsi = MeasureTrend(window=20, detect_width=8, use_ema=False)

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
        self.last_macd_diff = 0.0
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.buy_price_list = []
        self.buy_price = 0.0
        if not self.accnt.simulate:
            self.buy_price_list = self.accnt.load_buy_price_list(name, currency)
            if len(self.buy_price_list) > 0:
                self.buy_price = self.buy_price_list[-1]
        self.min_trade_size = self.base_min_size * 30.0
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
        if self.buy_price != 0.0: return

        # if we have insuffient funds to buy
        if self.accnt.simulate:
            balance_available = self.accnt.get_asset_balance_tuple(self.currency)[1]
            size = self.round_base(float(balance_available) / float(price))
        else:
            size=self.accnt.get_asset_balance(self.currency)['available']

        if size < self.min_trade_size:
            return

        if self.rsi_result > 38.0 and self.ema50.result < self.ema50.last_result < self.ema50.prev_last_result:
            return

        if self.rsi_result > 40.0:
            return

        if self.roc.last_result == 0.0 or self.roc.result < self.roc.last_result and self.ema26.prev_last_result < self.ema26.last_result < self.ema26.result:
            return

        ema12_roc = 0.0
        ema26_roc = 0.0

        if self.ema12.last_result != 0.0 and self.ema26.last_result != 0.0:
            ema12_roc = (self.ema12.result - self.ema12.last_result) / self.ema12.last_result
            ema26_roc = (self.ema26.result - self.ema26.last_result) / self.ema26.last_result
            if abs(ema12_roc) < abs(ema26_roc) / 2.0:
                return

        if self.ema50.last_result != 0.0 and self.ema26.last_result != 0.0:
            ema50_roc = (self.ema50.result - self.ema50.last_result) / self.ema50.last_result
            ema26_roc = (self.ema26.result - self.ema26.last_result) / self.ema26.last_result
            if abs(ema26_roc) < abs(ema50_roc) / 2.0:
                return

        if self.ema12.prev_last_result == 0.0 or self.ema12.prev_last_result > self.ema12.last_result > self.ema12.result:
            return

        if self.ema26.prev_last_result == 0.0 or self.ema26.prev_last_result > self.ema26.last_result > self.ema26.result:
            return

        if self.ema50.prev_last_result == 0.0 or self.ema50.prev_last_result > self.ema50.last_result > self.ema50.result:
            return

        if self.ema12.result > self.ema12.last_result > self.ema12.prev_last_result and self.roc.result < self.roc.last_result:
            return

        if self.ema26.result > self.ema26.last_result > self.ema26.prev_last_result and self.roc.result < self.roc.last_result:
            return

        if self.last_tsi_result == 0.0 or self.tsi.result < self.last_tsi_result:
            return

        if self.ema26.prev_last_result < self.ema26.last_result < self.ema26.result and self.ema_volume.result < self.ema_volume.last_result:
            return

        if self.cross_long.crossdown_detected() or self.cross_short.crossdown_detected() or not self.cross_short.crossup_detected():
            return

        result = self.accnt.buy_market(float(self.min_trade_size), price=price, ticker_id=self.get_ticker_id())
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            print("buy({}{}, {}) @ {} RSI={}".format(self.base, self.currency, self.min_trade_size, price, self.rsi_result))
            self.buy_price = price
            #self.buy_price_list.append(price)
            self.last_buy_price = price
        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def sell_signal(self, price):
        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < self.min_trade_size:
            return

        if self.buy_price == 0.0: return

        if self.buy_price != 0.0 and (price - self.buy_price) / self.buy_price < 0.01:
            return

        if self.rsi_result < 60.0 and self.tsi.result > self.last_tsi_result:
            return

        if self.roc.last_result == 0.0 or self.roc.result > self.roc.last_result:
            return

        if self.last_tsi_result == 0.0 or self.tsi.result > self.last_tsi_result:
            return

        if self.ema12.last_result != 0.0 and self.ema26.last_result != 0.0:
            ema12_roc = (self.ema12.result - self.ema12.last_result) / self.ema12.last_result
            ema26_roc = (self.ema26.result - self.ema26.last_result) / self.ema26.last_result
            if abs(ema12_roc) > abs(ema26_roc):
                return

        if self.ema12.prev_last_result == 0.0 or self.ema12.prev_last_result < self.ema12.last_result < self.ema12.result and \
           self.ema_volume.result > self.ema_volume.last_result:
            return

        if self.ema26.prev_last_result == 0.0 or self.ema26.prev_last_result < self.ema26.last_result < self.ema26.result and \
            self.ema_volume.result > self.ema_volume.last_result:
            return

        if self.ema50.prev_last_result == 0.0 or self.ema50.prev_last_result < self.ema50.last_result < self.ema50.result and \
           self.ema_volume.result > self.ema_volume.last_result:
            return

        if self.cross_long.crossup_detected() or self.cross_short.crossup_detected():
            return

        if self.last_tsi_result == 0.0 or self.tsi.result > self.last_tsi_result:
            return

        result = self.accnt.sell_market(float(self.min_trade_size), price=price, ticker_id=self.get_ticker_id())
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            pprofit = 100.0 * (price - self.buy_price) / self.buy_price
            print("sell({}{}, {}) @ {} (bought @ {}, {}%)".format(self.base, self.currency, self.min_trade_size,
                                                                  price, self.buy_price, round(pprofit, 2)))
            #self.buy_price_list.remove(buy_price)
            self.buy_price = 0.0
            self.last_sell_price = price
            if not self.accnt.simulate:
                total_usd, total_btc = self.accnt.get_account_total_value()
                print("Total balance USD = {}, BTC={}".format(total_usd, total_btc))
        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update(self, kline):
        self.ema_volume.update(float(kline['v']))
        self.run_update_price(float(kline['o']))
        self.rsi_result = self.rsi.update(float(kline['c']))
        self.roc.update(float(kline['c']), int(kline['E']))

        self.run_update_price(float(kline['c']))

        self.last_rsi_result = self.rsi_result

    def run_update_price(self, price):
        tsi_value = self.tsi.update(price)
        self.macd.update(price)
        value1 = self.ema12.update(price)
        value2 = self.ema26.update(price)
        value3 = self.ema50.update(price)
        value4 = self.ema100.update(price)
        self.cross_short.update(value1, value2)
        self.cross_long.update(value2, value3)

        self.buy_signal(price)
        self.sell_signal(price)
        self.last_macd_diff = self.macd.diff
        self.last_tsi_result = tsi_value

    def run_update_orderbook(self, msg):
        pass
    #    self.orderbook.process_update(msg)

    def close(self):
        #logger.info("close()")
        pass
