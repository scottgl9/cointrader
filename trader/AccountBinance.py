from trader.account.binance.client import Client
from trader.AccountBase import AccountBase
from datetime import datetime, timedelta

class AccountBinance(AccountBase):
    def __init__(self, client, name, asset, simulation=True):
        self.account_type = 'Binance'
        self.balance = 0.0
        self.funds_available = 0.0
        self.quote_currency_balance = 0.0
        self.quote_currency_available = 0.0
        self.base_currency = name
        self.currency = asset
        self.client = client
        self.simulate = simulation
        self.low_24hr = self.high_24hr = 0.0
        self.open_24hr = self.close_24hr = 0.0
        self.last_24hr = 0.0
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
        self.ticker_id = '{}{}'.format(name, asset)
        self.info = self.client.get_symbol_info(symbol=self.ticker_id)
        self.update_24hr_stats()

    def html_run_stats(self):
        results = str('')
        results += "quote_currency_balance: {}<br>".format(self.quote_currency_balance)
        results += "quote_currency_available: {}<br>".format(self.quote_currency_available)
        results += "balance: {}<br>".format(self.balance)
        results += "funds_available: {}<br>".format(self.funds_available)
        results += ("last: %f high: %f low: %f open: %f<br>" % (self.last_24hr,self.high_24hr, self.low_24hr, self.open_24hr))
        return results

    def round_base(self, price):
        return round(price, '{:f}'.format(self.base_min_size).index('1') - 1)

    def round_quote(self, price):
        return round(price, '{:f}'.format(self.quote_increment).index('1') - 1)

    def get_ticker_id(self):
        return '%s%s' % (self.base_currency, self.currency)

    def make_ticker_id(self, base, currency):
        return '%s%s' % (base, currency)

    def get_deposit_address(self):
        result = self.client.get_deposit_address(asset=self.base_currency)
        if 'success' in result and 'address' in result and result['success']:
            return result['address']
        return ''

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
        stats = self.client.get_ticker(symbol=self.ticker_id)

        self.high_24hr = self.low_24hr = self.open_24hr = 0.0

        if 'highPrice' in stats:
            self.high_24hr = float(stats['highPrice'])
        if 'lowPrice' in stats:
            self.low_24hr = float(stats['lowPrice'])
        if 'openPrice' in stats:
            self.open_24hr = float(stats['openPrice'])
        if 'lastPrice' in stats:
            self.last_24hr = self.close_24hr = float(stats['lastPrice'])

    def get_24hr_stats(self, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id

        stats = self.client.get_ticker(symbol=ticker_id)

        high_24hr = low_24hr = 0.0
        open_24hr = last_24hr = 0.0
        volume = 0.0
        ts_24hr = 0

        if 'highPrice' in stats:
            high_24hr = float(stats['highPrice'])
        if 'lowPrice' in stats:
            low_24hr = float(stats['lowPrice'])
        if 'openPrice' in stats:
            open_24hr = float(stats['openPrice'])
        if 'lastPrice' in stats:
            last_24hr = float(stats['lastPrice'])
        if 'volume' in stats:
            volume = float(stats['volume'])
        if 'openTime' in stats:
            ts_24hr = int(stats['openTime'])

        return {'l': low_24hr, 'h': high_24hr, 'o': open_24hr, 'c': last_24hr, 'v': volume, 't': ts_24hr}

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
        return self.client.get_all_orders(symbol=self.ticker_id, limit=100)

    def get_order(self, order_id):
        return self.client.get_order(order_id=order_id)

    def get_orders(self):
        return self.client.get_open_orders(symbol=self.ticker_id)

    def get_account_history(self):
        pass

    def get_my_trades(self, symbol, limit=500):
        return self.client.get_my_trades(symbol=symbol, limit=limit)

    def order_market_buy(self, symbol, quantity):
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def buy_market(self, size, ticker_id=None):
        if not self.simulate:
            if not ticker_id:
                ticker_id = self.ticker_id
            return self.client.create_test_order(symbol=ticker_id,
                                                 side=Client.SIDE_BUY,
                                                 type=Client.ORDER_TYPE_MARKET,
                                                 quantity=size)
        print("buy_market({})".format(size))

    def sell_market(self, size, ticker_id=None):
        if not self.simulate:
            if not ticker_id:
                ticker_id = self.ticker_id
            return self.client.create_test_order(symbol=ticker_id,
                                                 side=Client.SIDE_SELL,
                                                 type=Client.ORDER_TYPE_MARKET,
                                                 quantity=size)
        print("sell_market({})".format(size))

    def buy_limit_simulate(self, price, size):
        price = self.round_quote(price)
        size = self.round_base(size)

        print("buy_limit_simulate({}, {})".format(price, size))

        usd_value = self.round_quote(self.market_price * size)
        if usd_value <= 0.0: return
        if self.quote_currency_available >= usd_value:
            self.quote_currency_available -= usd_value
            return True
        return False

    def sell_limit_simulate(self, price, size):
        price = self.round_quote(price)
        size = self.round_base(size)
        print("sell_limit_simulate({}, {})".format(price, size))
        if size < self.base_min_size: return False
        if self.funds_available >= size:
            self.funds_available -= size
            return True
        return False

    def buy_limit(self, price, size, post_only=True, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id
        if self.simulate:
            return self.buy_limit_simulate(price, size)
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_buy(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)

    def sell_limit(self, price, size, post_only=True, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id
        if self.simulate:
            return self.sell_limit_simulate(price, size)
        timeInForce = Client.TIME_IN_FORCE_GTC
        return self.client.order_limit_sell(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)

    def cancel_order(self, orderid):
        return self.client.cancel_order(symbol=self.get_ticker_id(), orderId=orderid)

    def cancel_all(self):
        pass

    def get_klines(self, days=0, hours=1):
        timestr = ''
        if days == 1:
            timestr = "1 day ago"
        elif days > 1:
            timestr = "{} days ago".format(days)
        if days == 0:
            if hours == 1:
                timestr = "1 hour ago"
            elif hours > 1:
                timestr = "{} hours ago".format(hours)
        else:
            if hours == 1:
                timestr = "and 1 hour ago"
            elif hours > 1:
                timestr = "and {} hours ago".format(hours)
        timestr += " UTC"

        klines_data = self.client.get_historical_klines(self.ticker_id, Client.KLINE_INTERVAL_1MINUTE, timestr)

        # reorganize kline format to same as GDAX for consistency:
        # GDAX kline format: [ timestamp, low, high, open, close, volume ]
        # binance format: [opentime, open, high, low, close, volume, closetime quotevolume, tradecount,
        # taker_buy_base_volume, taker_buy_currency_volume, ignore]
        klines = []
        for k in klines_data:
            ts = k[0] / 1000
            klines.append([ts, k[3], k[2], k[1], k[4], k[5]])

        return klines
