from trader.account.AccountBaseBalance import AccountBaseBalance


class AccountCoinbaseBalance(AccountBaseBalance):
    def __init__(self, client, simulate=False, logger=None):
        self.client = client
        self.simulate = simulate
        self.logger = logger
        self.balances = {}

    def get_account_total_value(self, currency, detailed=False):
        raise NotImplementedError

    # implemented for CoinBase Pro
    def get_account_balances(self, detailed=False):
        if not self.simulate:
            self.balances = {}
            result = {}
            accounts = self.client.get_accounts()
            if 'message' in accounts:
                if self.logger:
                    self.logger.info("Error get_account_balances(): {}".format(accounts['message']))
                else:
                    print("Error get_account_balances(): {}".format(accounts['message']))
                return self.balances

            for account in accounts:
                asset_name = account['currency']
                balance = float(account['balance'])
                available = float(account['available'])
                hold = float(account['hold'])
                self.balances[asset_name] = {'balance': balance, 'available': available, 'hold': hold}
                result[asset_name] = balance
            if detailed:
                return self.balances
        else:
            if detailed:
                return self.balances
            result = {}
            for asset, info in self.balances.items():
                result[asset] = info['balance']
        return result

    def get_balances(self):
        return self.balances

    def get_asset_balance(self, asset):
        try:
            result = self.balances[asset]
        except KeyError:
            result = {'balance': 0.0, 'available': 0.0}
        return result

    def get_asset_balance_tuple(self, asset):
        result = self.get_asset_balance(asset)
        try:
            balance = float(result['balance'])
            available = float(result['available'])
        except KeyError:
            balance = 0.0
            available = 0.0
        if 'balance' not in result or 'available' not in result:
            return 0.0, 0.0
        return balance, available

    def update_asset_balance(self, name, balance, available):
        if self.simulate:
            if name in self.balances.keys() and balance == 0.0 and available == 0.0:
                del self.balances[name]
                return
            if name not in self.balances.keys():
                self.balances[name] = {}
            self.balances[name]['balance'] = balance
            self.balances[name]['available'] = available
