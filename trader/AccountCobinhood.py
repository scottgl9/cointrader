#from trader.account.cobinhood import
from trader.AccountBase import AccountBase


class AccountCobinhood(AccountBase):
    def __init__(self, client, name, asset):
        self.account_type = 'Cobinhood'
        self.balance = 0.0
        self.funds_available = 0.0
        self.quote_currency_balance = 0.0
        self.quote_currency_available = 0.0
        self.base_currency = name
        self.currency = asset
        self.client = client

        for funds in client.get_wallet_balances():
            if funds['asset'] == asset:
                self.quote_currency_balance = float(funds['free']) + float(funds['locked'])
                self.quote_currency_available = float(funds['free'])
            elif funds['asset'] == name:
                self.balance = float(funds['free']) + float(funds['locked'])
                self.funds_available = float(funds['free'])

        self.client = client
        self.ticker_id = self.get_ticker_id()
        #self.client.get_asset_balance()

    def html_run_stats(self):
        results = str('')
        results += "quote_currency_balance: {}<br>".format(self.quote_currency_balance)
        results += "quote_currency_available: {}<br>".format(self.quote_currency_available)
        results += "balance: {}<br>".format(self.balance)
        results += "funds_available: {}<br>".format(self.funds_available)
        #results += ("high: %f low: %f open: %f<br>" % (self.high_24hr, self.low_24hr, self.open_24hr))
        return results

    def get_ticker_id(self):
        return '%s%s' % (self.base_currency, self.currency)

    def handle_buy_completed(self, price, size):
        pass

    def handle_sell_completed(self, price, size):
        pass

    def get_orders(self):
        return self.client.get_all_orders(symbol=self.get_ticker_id(), limit=100)

    def get_open_orders(self, symbol):
        return self.client.get_open_orders(symbol=symbol)

    def cancel_order(self, order_id):
        return self.client.cancel_order(symbol=self.get_ticker_id(), orderId=order_id)

    def get_asset_balance(self, asset):
        return self.client.get_asset_balance(asset=asset)

    def get_account_status(self):
        return self.client.get_account_status()

    def update_account_balance(self, currency_balance, currency_available, balance, available):
        pass

    def get_account_balance(self):
        for funds in self.client.get_account()['balances']:
            if funds['asset'] == self.currency:
                self.quote_currency_balance = float(funds['free'])
            elif funds['asset'] == self.base_currency:
                self.base_currency_balance = float(funds['free'])
        return {"base_balance": self.base_currency_balance, "quote_balance": self.quote_currency_balance}

    def get_deposit_history(self, asset=None):
        return self.client.get_deposit_history(asset=asset)

    def get_my_trades(self, symbol, limit=500):
        return self.client.get_my_trades(symbol=symbol, limit=limit)

    def order_limit_buy(self, symbol, quantity, price, timeInForce=Client.TIME_IN_FORCE_GTC):
        return self.client.order_limit_buy(timeInForce=timeInForce, symbol=symbol, quantity=quantity, price=price)

    def order_limit_sell(self, symbol, quantity, price, timeInForce=Client.TIME_IN_FORCE_GTC):
        return self.client.order_limit_sell(timeInForce=timeInForce, symbol=symbol, quantity=quantity, price=price)

    def order_market_buy(self, symbol, quantity):
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def buy_market(self, size):
        return self.client.create_test_order(symbol=self.ticker_id, side=Client.SIDE_BUY, type=Client.ORDER_TYPE_MARKET, quantity=size)

    def sell_market(self, size):
        return self.client.create_test_order(symbol=self.ticker_id, side=Client.SIDE_SELL, type=Client.ORDER_TYPE_MARKET, quantity=size)

    def buy_limit(self, price, size, post_only=True):
        return self.order_limit_buy(symbol=self.ticker_id, price=price, quantity=size)

    def sell_limit(self, price, size, post_only=True):
        return self.order_limit_sell(symbol=self.ticker_id, price=price, quantity=size)