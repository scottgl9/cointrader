from trader.account.CryptoAccountBaseTrade import CryptoAccountBaseTrade
from trader.lib.struct.Exchange import Exchange

class AccountRobinhoodTrade(CryptoAccountBaseTrade):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.order_buy_crypto_by_quantity(ticker_id, size)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.order_buy_market(ticker_id, size)

    def sell_market(self, size, price=0.0, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.order_sell_crypto_by_quantity(ticker_id, size)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.order_sell_market(ticker_id, size)

    def buy_limit(self, price, size, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.order_buy_crypto_limit(ticker_id, size, price)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.order_buy_limit(ticker_id, size, price)

    def sell_limit(self, price, size, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.order_sell_crypto_limit(ticker_id, size, price)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.order_sell_limit(ticker_id, size, price)

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def get_order(self, order_id, ticker_id):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.get_crypto_order_info(order_id)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.get_stock_order_info(order_id)

    def get_orders(self, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            return self.client.get_all_open_crypto_orders()
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            return self.client.get_all_open_stock_orders()

    def cancel_order(self, orderid, ticker_id=None):
        mode = self.info.get_account_mode()
        if mode == Exchange.ACCOUNT_MODE_CRYPTO:
            self.client.cancel_crypto_order(orderid)
        elif mode == Exchange.ACCOUNT_MODE_STOCKS:
            self.client.cancel_stock_order(orderid)

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError
