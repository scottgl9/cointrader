from trader.account.binance import Client
from trader.AccountBase import AccountBase

class AccountBinance(AccountBase):
    def __init__(self, client, name, asset):
        self.account_type = 'Binance'
        self.balance = 0.0
        self.funds_available = 0.0
        self.quote_currency_balance = 0.0
        self.quote_currency_available = 0.0
        self.base_currency = name
        self.currency = asset
        self.client = client

        for funds in client.get_account()['balances']:
            if funds['asset'] == asset:
                self.quote_currency_balance = float(funds['free']) + float(funds['locked'])
                self.quote_currency_available = float(funds['free'])
            elif funds['asset'] == name:
                self.balance = float(funds['free']) + float(funds['locked'])
                self.funds_available = float(funds['free'])

        self.client = client
        self.ticker_id = self.get_ticker_id()
        self.info = self.client.get_symbol_info(symbol=self.ticker_id)
        stats = self.client.get_ticker(self.ticker_id)

        self.high_24hr = self.low_24hr = self.open_24hr = 0.0

        if 'highPrice' in stats:
            self.high_24hr = float(stats['highPrice'])
        if 'lowPrice' in stats:
            self.low_24hr = float(stats['lowPrice'])
        if 'openPrice' in stats:
            self.open_24hr = float(stats['openPrice'])

    def html_run_stats(self):
        results = str('')
        results += "quote_currency_balance: {}<br>".format(self.quote_currency_balance)
        results += "quote_currency_available: {}<br>".format(self.quote_currency_available)
        results += "balance: {}<br>".format(self.balance)
        results += "funds_available: {}<br>".format(self.funds_available)
        results += ("high: %f low: %f open: %f<br>" % (self.high_24hr, self.low_24hr, self.open_24hr))
        return results

    def get_ticker_id(self):
        return '%s%s' % (self.base_currency, self.currency)

    def get_deposit_address(self):
        return self.client.get_deposit_address(asset=self.get_ticker_id())

    def handle_buy_completed(self, price, size):
        pass

    def handle_sell_completed(self, price, size):
        pass

    def get_all_orders(self, symbol, limit=500):
        return self.client.get_all_orders(symbol=symbol, limit=limit)

    def get_open_orders(self, symbol):
        return self.client.get_open_orders(symbol=symbol)

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

    def cancel_order(self, orderid):
        return self.client.cancel_order(symbol=self.get_ticker_id(), orderId=orderid)
