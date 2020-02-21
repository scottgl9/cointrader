from trader.account.AccountBaseBalance import AccountBaseBalance

class AccountBittrexBalance(AccountBaseBalance):
    def __init__(self, client, simulation=False, logger=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger
        self.balances = {}

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
