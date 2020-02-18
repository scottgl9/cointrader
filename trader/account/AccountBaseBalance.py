# base account class for handling account balances

class AccountBaseBalance(object):
    def get_account_total_value(self, currency, detailed=False):
        pass

    def get_account_balances(self, detailed=False):
        pass

    def get_asset_balance_tuple(self, asset):
        return 0, 0

    def update_asset_balance(self, name, balance, available):
        pass
