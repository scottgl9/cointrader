from trader.account.yobit import YoBit

class AccountYoBit(object):
    def __init__(self, client, name, currency='USD'):
        if not client:
            self.client = YoBit()
        pass

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

    def get_price(self):
        pass

    def set_market_price(self, price):
        pass

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        pass

    def check_order_error(self, result, side):
        pass

    def get_order(self, order_id):
        pass

    def get_orders(self):
        pass

    def buy_limit_stop(self, price, size, stop_price, post_only=True):
        pass

    def buy_limit(self, price, size, post_only=True):
        pass

    def buy_market(self, size):
        pass

    def sell_limit_stop(self, price, size, stop_price, post_only=True):
        pass

    def sell_limit(self, price, size, post_only=True):
        pass

    def sell_market(self, size):
        pass

    def cancel_order(self, order_id):
        return self.client.cancel_order(order_id=order_id)

    def cancel_all(self):
        pass
