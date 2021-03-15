from trader.account.CryptoAccountBaseTrade import CryptoAccountBaseTrade

class AccountBittrexTrade(CryptoAccountBaseTrade):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        return self.client.trade_buy(market=ticker_id, order_type='MARKET', quantity=size)

    def sell_market(self, size, price=0.0, ticker_id=None):
        return self.client.trade_sell(market=ticker_id, order_type='MARKET', quantity=size)

    def buy_limit(self, price, size, ticker_id=None):
        return self.client.trade_buy(market=ticker_id,
                                     order_type='LIMIT',
                                     quantity=size,
                                     time_in_effect='GOOD_TIL_CANCELLED',
                                     condition_type='LESS_THAN',
                                     target=price)

    def sell_limit(self, price, size, ticker_id=None):
        return self.client.trade_sell(market=ticker_id,
                                      order_type='LIMIT',
                                      quantity=size,
                                      time_in_effect='GOOD_TIL_CANCELLED',
                                      condition_type='GREATER_THAN',
                                      target=price)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(orderId=order_id, symbol=ticker_id)

    def get_orders(self, ticker_id=None):
        return self.client.get_open_orders(symbol=ticker_id)

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel(uuid=orderid)

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
