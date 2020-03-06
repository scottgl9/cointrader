from trader.account.AccountBaseTrade import AccountBaseTrade

class AccountRobinhoodTrade(AccountBaseTrade):
    def __init__(self, client, simulation=False, logger=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        return self.client.order_buy_market(ticker_id, size)

    def sell_market(self, size, price=0.0, ticker_id=None):
        return self.client.order_sell_market(ticker_id, size)

    def buy_limit(self, price, size, ticker_id=None):
        return self.client.order_buy_limit(ticker_id, size, price)

    def sell_limit(self, price, size, ticker_id=None):
        return self.client.order_sell_limit(ticker_id, size, price)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        return self.client.order_buy_stop_limit(ticker_id, size, price, stop_price)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
         return self.client.order_sell_stop_limit(ticker_id, size, price, stop_price)

    def get_order(self, order_id, ticker_id):
        return self.client.get_order_info(order_id)

    def get_orders(self, ticker_id=None):
        return self.client.get_all_orders()

    def cancel_order(self, orderid, ticker_id=None):
        self.client.cancel_order(orderid)

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
