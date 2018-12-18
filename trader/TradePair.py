import threading
from trader.strategy import *

from trader.strategy.hybrid_signal_market_strategy import hybrid_signal_market_strategy
from trader.strategy.hybrid_signal_stop_loss_strategy import hybrid_signal_stop_loss_strategy
from trader.strategy.null_strategy import null_strategy


def select_strategy(sname, client, base='BTC', currency='USD', signal_names=None, account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
    if sname == 'hybrid_signal_market_strategy':
        return hybrid_signal_market_strategy(client, base, currency, signal_names, account_handler,  base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'hybrid_signal_stop_loss_strategy':
        return hybrid_signal_stop_loss_strategy(client, base, currency, signal_names, account_handler, base_min_size=base_min_size, tick_size=tick_size, logger=logger)
    elif sname == 'null_strategy':
        return null_strategy(client, base, currency, account_handler, signal_names, base_min_size=base_min_size, tick_size=tick_size, logger=logger)


# class to handle individual trade pair (ex. BTC/USD)
class TradePair(threading.Thread):
    def __init__(self, client, accnt, strategy_name, signal_names, base='BTC', currency='USD', base_min_size=0, tick_size=0, logger=None):
        super(TradePair, self).__init__()
        self.client = client
        self.accnt = accnt
        self.strategy_name = strategy_name
        self.signal_names = signal_names
        self.logger = logger
        #self.order_handler = order_handler
        self.base_name = base
        self.currency = currency
        self.base_min_size = base_min_size
        self.tick_size = tick_size
        self.ticker_id = self.accnt.make_ticker_id(base, currency)
        #print(self.accnt.get_fills(ticker_id=self.ticker_id))

        self.strategy = select_strategy(self.strategy_name,
                                        self.client,
                                        self.base_name,
                                        self.currency,
                                        signal_names=self.signal_names,
                                        account_handler=self.accnt,
                                        base_min_size=self.base_min_size,
                                        tick_size=self.tick_size,
                                        logger=self.logger)

        self.last_close = 0.0
        self.low_24hr = self.high_24hr = 0.0
        self.open_24hr = self.close_24hr = 0.0
        self.last_24hr = 0.0
        self.volume_24hr = 0.0
        self.quote_increment = 0.01
        self.base_min_size = 0.0
        self.market_price = 0.0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.count_prices_added = 0
        self.tickers = None
        self.tpprofit = 0

    def get_24hr_stats(self):
        stats = self.accnt.get_24hr_stats()
        self.low_24hr = stats['l']
        self.high_24hr = stats['h']
        self.open_24hr = stats['o']
        self.last_24hr = stats['c']
        self.volume_24hr = stats['v']

    def html_run_stats(self):
        return self.strategy.html_run_stats()

    def get_ticker_id(self):
        return self.ticker_id

    def buy_market(self, size):
        return self.accnt.buy_market(ticker_id=self.ticker_id, size=size)

    def sell_market(self, size):
        return self.accnt.sell_market(ticker_id=self.ticker_id, size=size)

    def get_klines(self, days=0, hours=1, ticker_id=None):
        return self.accnt.get_klines(days, hours, ticker_id)

    def set_market_price(self, price):
        self.market_price = price

    def set_buy_price_size(self, buy_price, buy_size, sig_id=0):
        self.strategy.set_buy_price_size(buy_price, buy_size, sig_id)

    ## mmkline is kline from MarketManager which is filtered and resampled
    def run_update(self, kline, mmkline=None, cache_db=None):
        self.last_close = self.strategy.last_close
        result = self.strategy.run_update(kline, mmkline, cache_db)
        self.last_50_prices = self.strategy.last_50_prices
        self.prev_last_50_prices = self.strategy.prev_last_50_prices
        self.count_prices_added = self.strategy.count_prices_added
        return result

    def clear_price_counter(self):
        self.strategy.count_prices_added = 0
        self.count_prices_added = 0

    #def run_update_price(self, price):
    #    #if self.base_name == 'QTUM' and float(price) == 10.0: return
    #    #print("run_update_price({}, {}, {}".format(self.base_name, self.currency, price))
    #    return self.strategy.run_update_price(price)

    def update_tickers(self, tickers):
        self.tickers = tickers
        self.strategy.update_tickers(tickers)

    def update_total_percent_profit(self, tpprofit):
        if tpprofit == 0:
            return
        self.tpprofit = tpprofit
        self.strategy.update_total_percent_profit(tpprofit)

    def mm_enabled(self):
        return self.strategy.mm_enabled
