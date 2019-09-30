#from abc import ABCMeta, abstractmethod
from trader.lib.struct.Order import Order


class AccountBase(object):
    EXCHANGE_UNKNOWN = 0
    EXCHANGE_BINANCE = 1
    EXCHANGE_CBPRO = 2
    EXCHANGE_BITTREX = 3
    EXCHANGE_KRAKEN = 4
    EXCHANGE_POLONIEX = 5

    def ts_to_seconds(self, ts):
        pass

    def is_hourly_ts(self, ts):
        pass

    def get_hourly_ts(self, ts):
        pass

    def seconds_to_ts(self, seconds):
        pass

    def hours_to_ts(self, hours):
        pass

    def get_hourly_table_name(self, symbol):
        pass

    def get_symbol_hourly_table(self, table_name):
        pass

    def make_ticker_id(self, base, currency):
        pass

    def split_ticker_id(self, symbol):
        pass

    def split_symbol(self, symbol):
        pass

    def get_symbol_base(self, symbol):
        pass

    def get_symbol_currency(self, symbol):
        pass

    def load_exchange_info(self):
        pass

    def get_exchange_info(self):
        pass

    def parse_exchange_info(self, pair_info, asset_info):
        pass

    def get_exchange_pairs(self):
        pass

    def is_exchange_pair(self, symbol):
        pass

    def is_asset_available(self, name):
        pass

    def get_account_total_value(self, currency, detailed=False):
        pass

    def get_account_balances(self, detailed=False):
        pass

    def buy_market(self, size, ticker_id=None):
        pass

    def sell_market(self, size, ticker_id=None):
        pass

    def buy_limit(self, price, size):
        pass

    def sell_limit(self, price, size):
        pass

    def buy_limit_complete(self, price, size, ticker_id=None):
        pass

    def sell_limit_complete(self, price, size, ticker_id=None):
        pass

    def cancel_order(self, orderid, ticker_id=None):
        pass

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        pass
