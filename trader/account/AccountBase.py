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
    def get_deposit_address(self):
        pass

    @abstractmethod
    def handle_buy_completed(self, price, size):
        pass

    @abstractmethod
    def handle_sell_completed(self, price, size):
        pass

    @abstractmethod
    def get_account_balance(self):
        pass

    @abstractmethod
    def get_account_history(self):
        pass

    #@abstractmethod
    #def set_market_price(self, price):
    #    pass

    #@abstractmethod
    #def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
    #    pass

    #@abstractmethod
    #def check_order_error(self, result, side):
    #    pass

    #@abstractmethod
    #def get_order(self, order_id):
    #    pass

    @abstractmethod
    def get_orders(self):
        pass

    @abstractmethod
    def buy_limit(self, price, size, post_only=True):
        pass

    @abstractmethod
    def buy_market(self, size, ticker_id=None):
        pass

    @abstractmethod
    def sell_limit(self, price, size, post_only=True):
        pass

    @abstractmethod
    def sell_market(self, size, ticker_id=None):
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        pass

    @abstractmethod
    def cancel_all(self):
        pass
