# Just an example on how to write an account plugin

from trader.account.AccountBase import AccountBase
from trader.account.AccountBaseInfo import AccountBaseInfo
from trader.account.AccountBaseBalance import AccountBaseBalance
from trader.account.AccountBaseTrade import AccountBaseTrade
from trader.account.AccountBaseMarket import AccountBaseMarket


class AccountExample(AccountBase):
    def __init__(self, client, simulate=False, live=False, logger=None, simulate_db_filename=None):
        super(AccountExample, self).__init__(client, simulate, live, simulate_db_filename)
        #self.exchange_type = AccountBase.EXCHANGE_EXAMPLE
        self.exchange_name = 'example'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulate
        self.live = live

        self.info = AccountExampleInfo(client, simulate, logger)
        self.balance = AccountExampleBalance(client, self.info, simulate, logger)
        self.trade = AccountExampleTrade(client, self.info, simulate, logger)
        self.market = AccountExampleMarket(client, self.info, simulate, logger)


class AccountExampleInfo(AccountBaseInfo):
    def __init__(self, client, simulate=False, logger=None, exchange_info_file=None):
        self.exchange_info_file = exchange_info_file
        self.client = client
        self.simulate = simulate
        self.logger = logger
        #self.exchange_type = AccountBase.EXCHANGE_EXAMPLE
        self.exchange_name = 'example'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)

    def make_ticker_id(self, base, currency):
        raise NotImplementedError

    def split_ticker_id(self, symbol):
        raise NotImplementedError

    def get_trade_fee(self):
        raise NotImplementedError

    def get_currencies(self):
        raise NotImplementedError

    def get_currency_trade_pairs(self):
        raise NotImplementedError

    def get_info_all_assets(self):
        raise NotImplementedError

    def get_details_all_assets(self):
        raise NotImplementedError

    def load_exchange_info(self):
        raise NotImplementedError

    def get_exchange_info(self):
        raise NotImplementedError

    def parse_exchange_info(self, pair_info, asset_info):
        raise NotImplementedError

    def get_exchange_pairs(self):
        raise NotImplementedError

    def is_exchange_pair(self, symbol):
        raise NotImplementedError

    def get_asset_info(self, symbol=None, base=None, currency=None):
        raise NotImplementedError

    def get_asset_status(self, name=None):
        raise NotImplementedError

    def is_asset_available(self, name):
        raise NotImplementedError

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        raise NotImplementedError


class AccountExampleBalance(AccountBaseBalance):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def get_account_total_value(self, currency, detailed=False):
        raise NotImplementedError

    def get_account_balances(self, detailed=False):
        raise NotImplementedError

    def get_balances(self):
        raise NotImplementedError

    def get_asset_balance(self, asset):
        raise NotImplementedError

    def get_asset_balance_tuple(self, asset):
        raise NotImplementedError

    def update_asset_balance(self, name, balance, available):
        raise NotImplementedError


class AccountExampleTrade(AccountBaseTrade):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def sell_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def buy_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def sell_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        raise NotImplementedError

    def get_order(self, order_id, ticker_id):
        raise NotImplementedError

    def get_orders(self, ticker_id=None):
        raise NotImplementedError

    def cancel_order(self, orderid, ticker_id=None):
        raise NotImplementedError

    def parse_order_update(self, result):
        raise NotImplementedError

    # parse json response to order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        raise NotImplementedError

class AccountExampleMarket(AccountBaseMarket):
    def __init__(self, client, info, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.simulate = simulate
        self.logger = logger

    def get_ticker(self, symbol):
        raise NotImplementedError

    def get_tickers(self):
        raise NotImplementedError

    def get_ticker_symbols(self, currency=None):
        raise NotImplementedError

    def get_min_tickers(self):
        raise NotImplementedError

    def get_max_tickers(self):
        raise NotImplementedError

    def update_ticker(self, symbol, price, ts):
        raise NotImplementedError

    def update_tickers(self, tickers):
        raise NotImplementedError

    def get_klines(self, days=0, hours=1, mode=None, ticker_id=None):
        raise NotImplementedError

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        raise NotImplementedError
