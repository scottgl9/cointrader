# base account class for handling account balances

class AccountBaseBalance(object):
    def get_account_total_value(self, currency, detailed=False):
        raise NotImplementedError

    def get_account_balances(self, detailed=False):
        raise NotImplementedError

    def get_asset_balance_tuple(self, asset):
        raise NotImplementedError

    def update_asset_balance(self, name, balance, available):
        raise NotImplementedError
