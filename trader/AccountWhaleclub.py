from trader.account.whaleclub import Client


class AccountWhaleclub(object):
    #    #def __init__(self, auth_client, name, currency='USD'):
    #    pass

    def get_ticker_id(self):
        pass

    def get_deposit_address(self):
        pass

    def handle_buy_completed(self, price, size):
        pass

    def handle_sell_completed(self, price, size):
        pass

    def get_account_balance(self):
        pass

    def get_account_history(self):
        pass

    def update_account_balance(self, currency_balance, currency_available, balance, available):
        pass

    def set_market_price(self, price):
        pass

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        pass

    #    #def check_order_error(self, result, side):
    #    pass

    def get_order(self, order_id):
        pass

    def get_orders(self):
        pass

    def buy_limit(self, price, size, post_only=True):
        pass

    def buy_market(self, size):
        pass

    def sell_limit(self, price, size, post_only=True):
        pass

    def sell_market(self, size):
        pass

    def cancel_order(self, order_id):
        pass

    def cancel_all(self):
        pass
