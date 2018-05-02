from trader.indicator.EMA import EMA
from trader.indicator.IchimokuCloud import IchimokuCloud
from trader.indicator.RSI import RSI
from trader.indicator.MACD import MACD
from trader.indicator.OBV import OBV
from trader.indicator.ROC import ROC
from trader.indicator.TSI import TSI
from trader.Crossover import Crossover
from trader.signal.EMA_OBV_Crossover import EMA_OBV_Crossover
from trader.signal.SignalHandler import SignalHandler
from trader.SupportResistLevels import SupportResistLevels
from trader.lib.StatTracker import StatTracker
from datetime import datetime
#import logging

#logger = logging.getLogger(__name__)


def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)


# compute if p1 is greater than p2 by X percent
def percent_p1_gt_p2(p1, p2, percent):
    if p1 == 0: return False
    result = 100.0 * (float(p1) - float(p2)) / float(p1)
    if result <= percent:
        return False
    return True


def percent_p2_gt_p1(p1, p2, percent):
    if p1 == 0: return False
    if p2 <= p1: return False
    result = 100.0 * (float(p2) - float(p1)) / float(p1)
    if result <= percent:
        return False
    return True


# compute if p1 is less than p2 by X percent (p1 is "threshold")
def percent_p1_lt_p2(p1, p2, percent):
    if p1 == 0: return False
    result = 100.0 * (float(p2) - float(p1)) / float(p1)
    if result >= percent:
        return False
    return True


class momentum_swing_strategy(object):
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0):
        self.strategy_name = 'momentum_swing_strategy'
        self.client = client
        self.accnt = account_handler
        self.ticker_id = self.accnt.make_ticker_id(name, currency)
        self.last_price = self.price = 0.0
        self.macd = MACD(12.0, 26.0, 9.0, scale=1.0)
        self.macd_result = 0.0
        self.last_macd_result = 0.0
        self.macd_diff = 0.0
        self.last_macd_diff = 0.0
        self.rsi = RSI()
        self.rsi_result = 0.0
        self.last_rsi_result = 0.0
        self.roc = ROC()
        self.tsi = TSI()
        self.last_tsi_result = 0.0

        self.signal_handler = SignalHandler()
        self.signal_handler.add(EMA_OBV_Crossover())

        self.roc_obv_ema = EMA(3, scale=1, lagging=True)

        self.levels = SupportResistLevels()
        self.low_short = self.high_short = 0.0
        self.low_long = self.high_long = 0.0
        self.prev_low_long = self.prev_high_long = 0.0
        self.prev_low_short = self.prev_high_short = 0.0

        self.cross_macd = Crossover()
        self.cross_macd_zero = Crossover()

        self.cloud = IchimokuCloud()
        self.SpanA = 0.0
        self.SpanB = 0.0
        self.cross_cloud = Crossover()
        self.stats = StatTracker()

        self.base = name
        self.currency = currency

        self.count_prices_added = 0
        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0
        self.last_timestamp = 0
        self.timestamp = 0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.trend_upward_count = 0
        self.trend_downward_count = 0
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.buy_price_list = []
        self.buy_price = 0.0
        self.last_price = 0.0
        #if not self.accnt.simulate:
        #    self.buy_price_list = self.accnt.load_buy_price_list(name, currency)
        #    if len(self.buy_price_list) > 0:
        #        self.buy_price = self.buy_price_list[-1]
        self.btc_trade_size = 0.0011
        self.eth_trade_size = 0.011
        self.bnb_trade_size = 0.71
        self.usdt_trade_size = 10.0
        self.min_trade_size = 0.0 #self.base_min_size * 20.0
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
        if self.base_min_size != 0.0:
            return round(price, '{:f}'.format(self.base_min_size).index('1') - 1)
        return price

    def round_quote(self, price):
        if self.quote_increment != 0.0:
            return round(price, '{:f}'.format(self.quote_increment).index('1') - 1)
        return price

    def my_float(self, value):
        return str("{:.8f}".format(float(value)))

    def place_buy_order(self, price):
        if 'e' in str(self.min_trade_size):
            return

        result = self.accnt.buy_market(self.min_trade_size, price=price, ticker_id=self.get_ticker_id())
        if not self.accnt.simulate:
            print(result)

        print("buy({}{}, {}) @ {}".format(self.base, self.currency, self.min_trade_size, price))
        if not self.accnt.simulate and not result:
            return

        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            self.buy_order_id = None
            if not self.accnt.simulate:
                if 'orderId' not in result:
                    print("WARNING: orderId not found for {}".format(self.ticker_id))
                    return
                orderid = result['orderId']
                self.buy_order_id = orderid
                #result = self.accnt.get_order(order_id=orderid, ticker_id=self.ticker_id)
                #if 'price' not in result:
                #    print("WARNING: price not found for {}".format(self.ticker_id))
                #    return
                #print(result)
                #if float(result['price']) != 0.0:
                #    price = result['price']
                #    print("buy({}{}, {}) @ {} (CORRECTED)".format(self.base, self.currency, self.min_trade_size, price))

            self.buy_price = price
            self.buy_size = self.min_trade_size
            #self.buy_price_list.append(price)
        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def place_sell_order(self, price):
        # get the actual buy price on the order before considering selling
        #if not self.accnt.simulate and self.buy_order_id:
        #    #result = self.accnt.get_order(order_id=self.buy_order_id, ticker_id=self.ticker_id)
        #    #if 'price' not in result:
        #    #    return
        #    #print(result)

        #    #if float(result['price']) != 0.0:
        #    #    self.buy_price = result['price']
        #    #    self.buy_order_id = None
        #    #    print("buy({}{}, {}) @ {} (CORRECTED)".format(self.base, self.currency, self.min_trade_size, self.buy_price))
        #    if price > self.buy_price:
        #        # assume that this is the actual price that the market order executed at
        #        print("Updated buy_price to {} from {}".format(price, self.buy_price))
        #        self.buy_price = price
        #        self.buy_order_id = None

        result = self.accnt.sell_market(self.buy_size, price=price, ticker_id=self.get_ticker_id())
        if not self.accnt.simulate and not result: return
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            pprofit = 100.0 * (price - self.buy_price) / self.buy_price
            print("sell({}{}, {}) @ {} (bought @ {}, {}%)".format(self.base, self.currency, self.buy_size,
                                                                  price, self.buy_price, round(pprofit, 2)))
            #self.buy_price_list.remove(buy_price)
            self.buy_price = 0.0
            self.buy_size = 0.0
            self.last_sell_price = price
            if not self.accnt.simulate:
                total_usd, total_btc = self.accnt.get_account_total_value()
                print("Total balance USD = {}, BTC={}".format(total_usd, total_btc))
        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def compute_min_trade_size(self, price):
        if self.ticker_id.endswith('BTC'):
            min_trade_size = self.round_base(self.btc_trade_size / price)
            if min_trade_size != 0.0:
                if self.base == 'ETH' or self.base == 'BNB':
                    self.min_trade_size = self.my_float(min_trade_size * 3)
                else:
                    self.min_trade_size = self.my_float(min_trade_size * 3)
                #print("{}: {} {} {}".format(self.ticker_id, self.min_trade_size, self.base_min_size, self.quote_increment))
        elif self.ticker_id.endswith('ETH'):
            min_trade_size = self.round_base(self.eth_trade_size / price)
            if min_trade_size != 0.0:
                if self.base == 'BNB':
                    self.min_trade_size = self.my_float(min_trade_size)
                else:
                    self.min_trade_size = self.my_float(min_trade_size)
        elif self.ticker_id.endswith('BNB'):
            min_trade_size = self.round_base(self.bnb_trade_size / price)
            if min_trade_size != 0.0:
                self.min_trade_size = self.my_float(min_trade_size)
        elif self.ticker_id.endswith('USDT'):
            min_trade_size = self.round_base(self.usdt_trade_size / price)
            if min_trade_size != 0.0:
                self.min_trade_size = self.my_float(min_trade_size)

    def buy_signal(self, price):
        if float(self.buy_price) != 0.0: return False

        if (self.timestamp - self.last_timestamp) > 500:
            return False

        # if we have insufficient funds to buy
        if self.accnt.simulate:
            balance_available = self.accnt.get_asset_balance_tuple(self.currency)[1]
            size = self.round_base(float(balance_available) / float(price))
        else:
            size=self.accnt.get_asset_balance(self.currency)['available']

        self.compute_min_trade_size(price)

        if float(self.min_trade_size) == 0.0 or size < float(self.min_trade_size):
            return False

        if self.last_buy_price != 0 and price > self.last_sell_price:
            return False

        if self.signal_handler.buy_signal():
            return True

        return False

    def sell_signal(self, price):
        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < float(self.min_trade_size):
            return False

        if float(self.buy_price) == 0.0:
            return False

        if not self.accnt.simulate and self.buy_order_id:
            #result = self.accnt.get_order(order_id=self.buy_order_id, ticker_id=self.ticker_id)
            #if 'price' not in result:
            #    return
            #print(result)

            #if float(result['price']) != 0.0:
            #    self.buy_price = result['price']
            #    self.buy_order_id = None
            #    print("buy({}{}, {}) @ {} (CORRECTED)".format(self.base, self.currency, self.min_trade_size, self.buy_price))
            if price > float(self.buy_price):
                # assume that this is the actual price that the market order executed at
                print("Updated buy_price to {} from {}".format(price, self.buy_price))
                self.buy_price = price
                self.buy_order_id = None
                return False

        if price < float(self.buy_price):
            return False

        #if self.rsi_result == 0.0 or self.rsi_result < 60.0:
        #    return False

        if self.base == 'ETH' or self.base == 'BNB':
            if not percent_p2_gt_p1(self.buy_price, price, 1.0):
                return False
        else:
            if not percent_p2_gt_p1(self.buy_price, price, 1.0):
                return False

        if self.signal_handler.sell_signal():
            return True

        return False

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]
        self.count_prices_added += 1

    # NOTE: low and high do not update for each kline with binance
    def run_update(self, kline):
        # HACK REMOVE THIS
        if self.currency == 'USDT':
            return
        close = float(kline['c'])
        low = float(kline['l'])
        high = float(kline['h'])
        volume = float(kline['v'])
        if close == 0 or volume == 0:
            return

        self.timestamp = int(kline['E'])
        #self.ema_volume.update(float(kline['v']))
        self.rsi_result = self.rsi.update(close)
        #self.last_macd_result = self.macd_result
        #self.macd_result = self.macd.update(close)
        #self.last_macd_diff = self.macd_diff
        #self.macd_diff = self.macd.diff
        #self.cross_macd.update(self.macd.diff, self.macd.signal.result)
        #self.cross_macd_zero.update(self.macd.diff, 0.0)
        #self.stats.update(close, self.timestamp)

        self.signal_handler.pre_update(close=close, volume=volume)

        self.run_update_price(close)

        self.last_rsi_result = self.rsi_result
        self.last_timestamp = self.timestamp
        self.last_price = close

    def run_update_price(self, price):
        if self.buy_signal(price):
            self.place_buy_order(price)
        if self.sell_signal(price):
            self.place_sell_order(price)
            self.last_sell_price = price

    def run_update_orderbook(self, msg):
        pass

    def close(self):
        #logger.info("close()")
        pass
