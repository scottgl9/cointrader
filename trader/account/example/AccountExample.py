# Just an example on how to write an account plugin

from trader.account.AccountBase import AccountBase
from trader.account.AccountBaseInfo import AccountBaseInfo
from trader.account.AccountBaseBalance import AccountBaseBalance
from trader.account.AccountBaseTrade import AccountBaseTrade


class AccountExample(AccountBase):
    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        super(AccountExample, self).__init__(client, simulation, logger, simulate_db_filename)
        #self.exchange_type = AccountBase.EXCHANGE_EXAMPLE
        self.exchange_name = 'example'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation

        self.info = AccountExampleInfo(client, simulation, logger, simulate_db_filename)
        self.balance = AccountExampleBalance(client, simulation, logger, simulate_db_filename)
        self.trade = AccountExampleTrade(client, simulation, logger, simulate_db_filename)


class AccountExampleInfo(AccountBaseInfo):
    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation
        self.logger = logger

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

    def is_asset_available(self, name):
        raise NotImplementedError


class AccountExampleBalance(AccountBaseBalance):
    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation
        self.logger = logger

    def get_account_total_value(self, currency, detailed=False):
        raise NotImplementedError

    def get_account_balances(self, detailed=False):
        raise NotImplementedError

    def get_asset_balance_tuple(self, asset):
        raise NotImplementedError

    def update_asset_balance(self, name, balance, available):
        raise NotImplementedError


class AccountExampleTrade(AccountBaseTrade):
    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation
        self.logger = logger

    def buy_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def sell_market(self, size, price=0.0, ticker_id=None):
        raise NotImplementedError

    def buy_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def sell_limit(self, price, size, ticker_id=None):
        raise NotImplementedError

    def cancel_order(self, orderid, ticker_id=None):
        raise NotImplementedError
