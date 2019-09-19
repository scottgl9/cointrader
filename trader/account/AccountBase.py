from abc import ABCMeta, abstractmethod


class AccountBase(object):
    __metaclass__ = ABCMeta

    #@abstractmethod
    #def __init__(self, auth_client, name, currency='USD'):
    #    pass

    #@abstractmethod
    #def get_ticker_id(self):
    #    pass

    @abstractmethod
    def make_ticker_id(self, base, currency):
        pass

    @abstractmethod
    def split_ticker_id(self, symbol):
        pass

    @abstractmethod
    def split_symbol(self, symbol):
        pass

    @abstractmethod
    def get_symbol_base(self, symbol):
        pass

    @abstractmethod
    def get_symbol_currency(self, symbol):
        pass

    @abstractmethod
    def get_account_balances(self, detailed=False):
        pass

    @abstractmethod
    def get_deposit_address(self):
        pass

    @abstractmethod
    def get_orders(self):
        pass

    @abstractmethod
    def buy_market(self, size, ticker_id=None):
        pass

    @abstractmethod
    def sell_market(self, size, ticker_id=None):
        pass

    @abstractmethod
    def buy_limit(self, price, size, post_only=True):
        pass

    @abstractmethod
    def sell_limit(self, price, size, post_only=True):
        pass

    @abstractmethod
    def buy_limit_complete(self, price, size, ticker_id=None):
        pass

    @abstractmethod
    def sell_limit_complete(self, price, size, ticker_id=None):
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        pass

    @abstractmethod
    def cancel_all(self):
        pass

    @abstractmethod
    def get_hourly_klines(self, symbol, start_ts, end_ts):
        pass
