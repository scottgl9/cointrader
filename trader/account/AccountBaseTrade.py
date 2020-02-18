# base account class for handling account executed trades

class AccountBaseTrade(object):
    def buy_market(self, size, price=0.0, ticker_id=None):
        pass

    def sell_market(self, size, price=0.0, ticker_id=None):
        pass

    def buy_limit(self, price, size, ticker_id=None):
        pass

    def sell_limit(self, price, size, ticker_id=None):
        pass

    def cancel_order(self, orderid, ticker_id=None):
        pass
