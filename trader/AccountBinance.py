from trader.account.binance.client import Client
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
        self.simulate = False
        self.low_24hr = self.high_24hr = 0.0
        self.open_24hr = self.close_24hr = 0.0
        self.volume_24hr = 0.0
        self.quote_increment = 0.01
        self.base_min_size = 0.0
        self.market_price = 0.0

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
        #stats = self.client.get_ticker(self.ticker_id)

        #self.high_24hr = self.low_24hr = self.open_24hr = 0.0

        #if 'highPrice' in stats:
        #    self.high_24hr = float(stats['highPrice'])
        #if 'lowPrice' in stats:
        #    self.low_24hr = float(stats['lowPrice'])
        #if 'openPrice' in stats:
        #    self.open_24hr = float(stats['openPrice'])

    def html_run_stats(self):
        results = str('')
        results += "quote_currency_balance: {}<br>".format(self.quote_currency_balance)
        results += "quote_currency_available: {}<br>".format(self.quote_currency_available)
        results += "balance: {}<br>".format(self.balance)
        results += "funds_available: {}<br>".format(self.funds_available)
        results += ("high: %f low: %f open: %f<br>" % (self.high_24hr, self.low_24hr, self.open_24hr))
        return results

    def round_base(self, price):
        return round(price, '{:f}'.format(self.base_min_size).index('1') - 1)

    def round_quote(self, price):
        return round(price, '{:f}'.format(self.quote_increment).index('1') - 1)

    def get_ticker_id(self):
        return '%s%s' % (self.base_currency, self.currency)

    def get_deposit_address(self):
        return self.client.get_deposit_address(asset=self.get_ticker_id())

    def handle_buy_completed(self, order_price, order_size):
        if not self.simulate: return
        self.quote_currency_balance -= self.round_quote(order_price * order_size)
        self.balance += order_size
        self.funds_available += order_size

    def handle_sell_completed(self, order_price, order_size):
        if not self.simulate: return
        usd_value = self.round_quote(order_price * order_size)
        self.quote_currency_available += usd_value
        self.quote_currency_balance += usd_value
        self.balance -= order_size

    def get_open_buy_orders(self):
        return []

    def get_open_sell_orders(self):
        return []

    def preload_buy_price_list(self):
        return [], []

    def update_24hr_stats(self):
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
        if self.simulate:
            self.quote_currency_balance = currency_balance
            self.quote_currency_available = currency_available
            self.balance = balance
            self.funds_available = available

    def get_account_balance(self):
        self.balance = 0.0
        for funds in self.client.get_account()['balances']:
            if funds['asset'] == self.currency:
                self.quote_currency_balance = float(funds['free']) + float(funds['locked'])
            elif funds['asset'] == self.base_currency:
                self.balance = float(funds['free']) + float(funds['locked'])
        return {"base_balance": self.balance, "quote_balance": self.quote_currency_balance}

    def get_deposit_history(self, asset=None):
        return self.client.get_deposit_history(asset=asset)

    def set_market_price(self, price):
        self.market_price = price

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        pass

    def get_order(self, order_id):
        return self.client.get_order(order_id=order_id)

    def get_orders(self):
        pass

    def get_account_history(self):
        pass

    def get_my_trades(self, symbol, limit=500):
        return self.client.get_my_trades(symbol=symbol, limit=limit)

    def order_market_buy(self, symbol, quantity):
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def buy_market(self, size):
        if not self.simulate:
            return self.client.create_test_order(symbol=self.ticker_id,
                                                 side=Client.SIDE_BUY,
                                                 type=Client.ORDER_TYPE_MARKET,
                                                 quantity=size)

    def sell_market(self, size):
        if not self.simulate:
            return self.client.create_test_order(symbol=self.ticker_id,
                                                 side=Client.SIDE_SELL,
                                                 type=Client.ORDER_TYPE_MARKET,
                                                 quantity=size)

    def buy_limit_simulate(self, price, size):
        price = self.round_quote(price)
        size = self.round_base(size)

        usd_value = self.round_quote(self.market_price * size)
        if usd_value <= 0.0: return
        if self.quote_currency_available >= usd_value:
            self.quote_currency_available -= usd_value
            return True
        return False

    def sell_limit_simulate(self, price, size):
        price = self.round_quote(price)
        size = self.round_base(size)
        if size < self.base_min_size: return False
        if self.funds_available >= size:
            self.funds_available -= size
            return True
        return False

    def buy_limit(self, price, size, post_only=True):
        if self.simulate:
            return self.buy_limit_simulate(price, size)
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_buy(timeInForce=timeInForce, symbol=self.ticker_id, quantity=size, price=price)

    def sell_limit(self, price, size, post_only=True):
        if self.simulate:
            return self.sell_limit_simulate(price, size)
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_sell(timeInForce=timeInForce, symbol=self.ticker_id, quantity=size, price=price)

    def cancel_order(self, orderid):
        return self.client.cancel_order(symbol=self.get_ticker_id(), orderId=orderid)

    def cancel_all(self):
        pass
