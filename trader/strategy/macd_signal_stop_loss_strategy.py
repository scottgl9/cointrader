from trader.lib.MessageHandler import Message, MessageHandler
from trader.signal.MACD_Crossover import MACD_Crossover
from trader.signal.OBV_Crossover import OBV_Crossover
from trader.signal.SignalHandler import SignalHandler
from trader.indicator.OBV import OBV
from trader.lib.SupportResistLevels import SupportResistLevels
from trader.lib.StatTracker import StatTracker
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


class macd_signal_stop_loss_strategy(object):
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None, base_min_size=0.0, tick_size=0.0, rank=None, logger=None):
        self.strategy_name = 'macd_signal_stop_loss_strategy'
        self.logger = logger
        self.client = client
        self.accnt = account_handler
        self.rank = rank
        self.ticker_id = self.accnt.make_ticker_id(name, currency)
        self.last_price = self.price = 0.0
        self.last_close = 0.0

        self.msg_handler = MessageHandler()
        self.signal_handler = SignalHandler(logger=logger)
        self.signal_handler.add(MACD_Crossover())

        self.obv = OBV()
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
        self.timestamp = 0
        self.last_timestamp = 0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0
        self.last_buy_ts = 0
        self.last_buy_obv = 0
        self.last_sell_ts = 0
        self.last_sell_obv = 0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.trend_upward_count = 0
        self.trend_downward_count = 0
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.buy_price_list = []
        self.buy_price = 0.0
        self.buy_size = 0.0
        self.buy_timestamp = 0
        self.buy_order_id = None
        self.last_price = 0.0
        self.buy_pending = False
        self.sell_pending = False
        #if not self.accnt.simulate:
        #    self.buy_price_list = self.accnt.load_buy_price_list(name, currency)
        #    if len(self.buy_price_list) > 0:
        #        self.buy_price = self.buy_price_list[-1]
        self.btc_trade_size = 0.0011
        self.eth_trade_size = 0.011
        self.bnb_trade_size = 0.8
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

        # if more than 500 seconds between price updates, ignore signal
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
            return True

        return False


    def sell_signal(self, price):
        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < float(self.min_trade_size):
            return False

        if float(self.buy_price) == 0.0:
            return False

        if price < float(self.buy_price):
            return False

        if self.base == 'ETH' or self.base == 'BNB':
            if not percent_p2_gt_p1(self.buy_price, price, 1.0):
                return False
        else:
            if not percent_p2_gt_p1(self.buy_price, price, 1.0):
                return False

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


    def set_buy_price_size(self, buy_price, buy_size):
        if self.buy_price == 0:
            self.buy_price = buy_price
        if self.buy_size == 0:
            self.buy_size = buy_size
        print("loading into {} price={} size={}".format(self.ticker_id, buy_price, buy_size))


    # NOTE: low and high do not update for each kline with binance
    def run_update(self, kline):
        # HACK REMOVE THIS
        #if self.currency == 'USDT':
        #    return
        close = float(kline['c'])
        low = float(kline['l'])
        high = float(kline['h'])
        volume = float(kline['v'])

        if close == 0 or volume == 0:
            return

        self.timestamp = int(kline['E'])

        self.obv.update(close, volume)

        self.signal_handler.pre_update(close=close, volume=volume, ts=self.timestamp)

        self.run_update_price(close)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close


    def run_update_price(self, price):
        if not self.buy_pending and self.buy_signal(price):
            if 'e' in str(self.min_trade_size):
                return

            min_trade_size = self.min_trade_size

            if self.min_trade_size_qty != 1.0:
                min_trade_size = float(min_trade_size) * self.min_trade_size_qty

            buy_price = price + self.quote_increment
            buy_size = min_trade_size

            self.msg_handler.buy_stop_loss(self.ticker_id, buy_price, buy_size)
            self.buy_pending = True

        if not self.sell_pending and self.sell_signal(price):
            sell_price = price - self.quote_increment
            self.msg_handler.sell_stop_loss(self.ticker_id, sell_price, self.buy_size, self.buy_price)
            self.sell_pending = True

            if self.min_trade_size_qty != 1.0:
                self.min_trade_size_qty = 1.0

        if self.buy_pending:
            msg = self.msg_handler.get_first_message(src_id=Message.ID_MULTI, dst_id=self.ticker_id)
            if not msg: return
            self.buy_price = float(msg.price)
            self.buy_size = float(msg.size)
            self.buy_timestamp = self.timestamp
            self.last_buy_ts = self.timestamp
            self.last_buy_obv = self.obv.result
            self.buy_pending = False
            msg.mark_read()
        elif self.sell_pending:
            msg = self.msg_handler.get_first_message(src_id=Message.ID_MULTI, dst_id=self.ticker_id)
            if not msg: return
            self.last_buy_price = self.buy_price
            self.buy_price = 0.0
            self.buy_size = 0.0
            self.last_sell_price = msg.price
            self.last_sell_ts = self.timestamp
            self.last_sell_obv = self.obv.result
            self.buy_timestamp = 0
            self.sell_pending = False
            msg.mark_read()


    def run_update_orderbook(self, msg):
        pass


    def close(self):
        #logger.info("close()")
        pass
