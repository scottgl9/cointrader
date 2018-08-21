from trader.lib.Message import Message
from trader.lib.MessageHandler import MessageHandler
from trader.signal.MACD_Crossover import MACD_Crossover
from trader.signal.EMA_OBV_Crossover import EMA_OBV_Crossover
from trader.signal.RSI_OBV import RSI_OBV
from trader.signal.TD_Sequential_Signal import TD_Sequential_Signal
from trader.signal.TSI_Signal import TSI_Signal
from trader.signal.price_channel_signal import price_channel_signal
from trader.signal.SignalHandler import SignalHandler
from trader.lib.StatTracker import StatTracker
from trader.lib.OrderTrack import OrderTrack
from datetime import datetime


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
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0, rank=None):
        self.strategy_name = 'momentum_swing_strategy'
        self.client = client
        self.accnt = account_handler
        self.rank = rank
        self.ticker_id = self.accnt.make_ticker_id(name, currency)
        self.last_price = self.price = 0.0
        self.last_close = 0.0

        self.order_track = OrderTrack(OrderTrack.MARKET_ORDER, max_order_count=1, percent=0.7)
        self.msg_handler = MessageHandler()
        self.signal_handler = SignalHandler()
        #self.signal_handler.add(RSI_OBV())
        #self.signal_handler.add(PPO_OBV())
        #self.signal_handler.add(TSI_Signal())
        self.signal_handler.add(MACD_Crossover())
        #self.signal_handler.add(price_channel_signal())
        #self.signal_handler.add(TD_Sequential_Signal())
        #self.signal_handler.add(EMA_OBV_Crossover())
        #self.signal_handler.add(BOX_OBV())

        self.low_short = self.high_short = 0.0
        self.low_long = self.high_long = 0.0
        self.prev_low_long = self.prev_high_long = 0.0
        self.prev_low_short = self.prev_high_short = 0.0

        self.stats = StatTracker()

        self.base = name
        self.currency = currency

        self.count_prices_added = 0
        self.buy_signal_count = self.sell_signal_count = 0
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.rank_value = -1
        self.last_rank_value = -1
        self.rank_increases = 0
        self.rank_decreases = 0
        self.rank_top = False
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
        self.buy_size = 0.0
        self.buy_order_id = None
        self.last_price = 0.0
        #if not self.accnt.simulate:
        #    self.buy_price_list = self.accnt.load_buy_price_list(name, currency)
        #    if len(self.buy_price_list) > 0:
        #        self.buy_price = self.buy_price_list[-1]
        self.btc_trade_size = 0.0011
        self.eth_trade_size = 0.011
        self.bnb_trade_size = 1.0
        self.usdt_trade_size = 10.0
        self.min_trade_size = 0.0 #self.base_min_size * 20.0
        self.min_trade_size_qty = 1.0
        #self.accnt.get_account_balances()
        self.tickers = None
        self.min_price = 0.0
        self.max_price = 0.0

    def get_ticker_id(self):
        return self.ticker_id

    # clear pending sell trades which have been bought
    def reset(self):
        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_order_id = None

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
            return round(price, '{:.9f}'.format(self.base_min_size).index('1') - 1)
        return price

    def round_quote(self, price):
        if self.quote_increment != 0.0:
            return round(price, '{:.9f}'.format(self.quote_increment).index('1') - 1)
        return price

    def my_float(self, value):
        return str("{:.9f}".format(float(value)))

    def compute_min_trade_size(self, price):
        if self.ticker_id.endswith('BTC'):
            min_trade_size = self.round_base(self.btc_trade_size / price)
            if min_trade_size != 0.0:
                if self.base == 'ETH' or self.base == 'BNB':
                    self.min_trade_size = self.my_float(min_trade_size * 3)
                else:
                    self.min_trade_size = self.my_float(min_trade_size * 3)
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

        if self.last_close == 0:
            return False

        # do not buy back in the previous buy/sell price range
        if self.last_buy_price != 0 and self.last_sell_price != 0:
            if self.last_buy_price <= price <= self.last_sell_price:
                return False

        if self.signal_handler.buy_signal():
            #if self.rank_decreases >= self.rank_increases:
            #    return False
            #if self.last_roc != 0.0 and self.roc != 0.0 and self.roc > self.last_roc:
            #    self.min_trade_size_qty = 3.0
            #if self.rank_increases > self.rank_decreases:
            return True

        return False

    def sell_signal(self, price):
        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < float(self.min_trade_size):
            return False

        #if float(self.buy_price) == 0.0:
        #    return False

        if not self.accnt.simulate and self.buy_order_id:
            if price > float(self.buy_price):
                # assume that this is the actual price that the market order executed at
                print("Updated buy_price from {} to {}".format(self.buy_price, price))
                self.buy_price = price
                self.buy_order_id = None
                return False

        #if self.rank_top and self.ticker_id in dict(self.rank.rank_descending_bottom()).keys() and self.signal_handler.sell_signal():
        #    self.rank_top = False
        #    pchange = (price - self.buy_price) / self.buy_price
        #    if pchange >= 0.0:
        #        return True

        #if price < float(self.buy_price):
        #    return False

        #if self.base == 'ETH' or self.base == 'BNB':
        #    if not percent_p2_gt_p1(self.buy_price, price, 0.1):
        #        return False
        #else:
        #    if not percent_p2_gt_p1(self.buy_price, price, 0.1):
        #        return False

        if self.signal_handler.sell_signal():
            self.rank_increases = 0
            self.rank_decreases = 0
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

        self.last_rank_value = self.rank_value
        self.rank_value = self.rank.rank(symbol=self.ticker_id)
        if self.last_rank_value != -1 and self.rank_value != -1:
            if self.rank_value < self.last_rank_value:
                self.rank_decreases += (self.last_rank_value - self.rank_value)
            elif self.rank_value > self.last_rank_value:
                self.rank_increases += (self.rank_value - self.last_rank_value)

        self.signal_handler.pre_update(close=close, volume=volume, ts=self.timestamp)

        self.run_update_price(close)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close

    def run_update_price(self, price):
        if self.order_track.can_buy() and self.buy_signal(price):
            if 'e' in str(self.min_trade_size):
                return

            min_trade_size = self.min_trade_size

            if self.min_trade_size_qty != 1.0:
                min_trade_size = float(min_trade_size) * self.min_trade_size_qty

            self.buy_price = price
            self.buy_size = min_trade_size

            self.msg_handler.buy_market(self.ticker_id, price, self.buy_size)
            self.order_track.buy(price, self.buy_size)
        if self.order_track.can_sell() and self.sell_signal(price):
            size = self.order_track.sell(price)
            if size != 0.0:
                self.msg_handler.sell_market(self.ticker_id, price, self.buy_size, self.buy_price)

                if self.min_trade_size_qty != 1.0:
                    self.min_trade_size_qty = 1.0

                self.last_buy_price = self.buy_price
                self.buy_price = 0.0
                self.buy_size = 0.0
                self.last_sell_price = price

    def run_update_orderbook(self, msg):
        pass

    def close(self):
        #logger.info("close()")
        pass
