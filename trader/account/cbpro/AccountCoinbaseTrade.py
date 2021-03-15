from trader.account.CryptoAccountBaseTrade import CryptoAccountBaseTrade
from trader.account.binance.binance.client import Client, BinanceAPIException
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate


class AccountCoinbaseTrade(AccountBaseTrade):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        return self.client.place_market_order(product_id=ticker_id, side='buy', size=size)

    def sell_market(self, size, price=0.0, ticker_id=None):
        return self.client.place_market_order(product_id=ticker_id, side='sell', size=size)

    def buy_limit(self, price, size, ticker_id=None):
        return self.client.place_limit_order(product_id=ticker_id, side='buy', price=price, size=size)

    def sell_limit(self, price, size, ticker_id=None):
        return self.client.place_limit_order(product_id=ticker_id, side='sell', price=price, size=size)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        return self.client.place_stop_order(product_id=ticker_id, side='buy', price=price, size=size)

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        return self.client.place_stop_order(product_id=ticker_id, side='sell', price=price, size=size)

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(order_id=order_id)

    def get_orders(self, ticker_id=None):
        raise NotImplementedError

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_order(order_id=orderid)

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
