#from abc import ABCMeta, abstractmethod
from trader.lib.struct.Order import Order


class AccountBase(object):
    # __metaclass__ = ABCMeta

    #@abstractmethod
    #def __init__(self, auth_client, name, currency='USD'):
    #    pass

    #@abstractmethod
    #def get_ticker_id(self):
    #    pass

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

    def get_account_balances(self, detailed=False):
        pass

    def get_deposit_address(self):
        pass

    def get_orders(self):
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

    def cancel_order(self, order_id):
        pass

    def cancel_all(self):
        pass

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        pass
