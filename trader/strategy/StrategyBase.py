# base class for all strategies
from datetime import datetime
from trader.lib.MessageHandler import Message, MessageHandler
from trader.signal.SignalHandler import SignalHandler

class StrategyBase(object):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
        self.strategy_name = None
        self.logger = logger
        self.tickers = None
        self.base = base
        self.currency = currency
        self.ticker_id = None
        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.client = client
        self.accnt = account_handler
        self.make_ticker_id()
        self.msg_handler = MessageHandler()
        self.signal_handler = SignalHandler(self.ticker_id, logger=logger)
        self.trade_size_handler = None
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.count_prices_added = 0
        self.mm_enabled = False
        self.kline = None

    def get_ticker_id(self):
        return self.ticker_id

    def make_ticker_id(self):
        if self.accnt:
            self.ticker_id = self.accnt.make_ticker_id(self.base, self.currency)

    def get_signals(self):
        if self.signal_handler:
            return self.signal_handler.get_handlers()
        return None

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

    def reset(self):
        pass

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]
        #self.count_prices_added += 1

    def buy_signal(self, signal, price):
        pass

    def sell_signal(self, signal, price):
        pass

    def set_buy_price_size(self, buy_price, buy_size, sig_id=0):
        pass

    ## mmkline is kline from MarketManager which is filtered and resampled
    def run_update(self, kline, mmkline=None):
        pass

    def run_update_signal(self, signal, price):
        pass

    def run_update_orderbook(self, msg):
        pass

    def update_tickers(self, tickers):
        self.tickers = tickers
        if self.trade_size_handler:
            self.trade_size_handler.update_tickers(tickers)

    def close(self):
        pass

    @staticmethod
    def datetime_to_float(d):
        epoch = datetime.utcfromtimestamp(0)
        total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
        # total_seconds will be in decimals (millisecond precision)
        return float(total_seconds)

    # compute if p1 is greater than p2 by X percent
    @staticmethod
    def percent_p1_gt_p2(p1, p2, percent):
        if p1 == 0: return False
        result = 100.0 * (float(p1) - float(p2)) / float(p1)
        if result <= percent:
            return False
        return True

    @staticmethod
    def percent_p2_gt_p1(p1, p2, percent):
        if p1 == 0: return False
        if p2 <= p1: return False
        result = 100.0 * (float(p2) - float(p1)) / float(p1)
        if result <= percent:
            return False
        return True

    # compute if p1 is less than p2 by X percent (p1 is "threshold")
    @staticmethod
    def percent_p1_lt_p2(p1, p2, percent):
        if p1 == 0: return False
        result = 100.0 * (float(p2) - float(p1)) / float(p1)
        if result >= percent:
            return False
        return True
