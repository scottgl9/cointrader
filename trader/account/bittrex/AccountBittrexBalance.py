from trader.account.CryptoAccountBaseBalance import CryptoAccountBaseBalance

class AccountBittrexBalance(CryptoAccountBaseBalance):
    def __init__(self, client, info, market, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.market = market
        self.simulate = simulate
        self.logger = logger
        self.balances = {}

    def get_account_total_value(self, currency, detailed=False):
        raise NotImplementedError

    def get_account_balances(self, detailed=False):
        self.balances = {}
        result = {}

        info_balances = self.client.get_balances()
        if not info_balances['success']:
            return self.balances
        for info in info_balances['result']:
            cinfo = info['Currency']
            if not cinfo['IsActive'] or cinfo['IsDeleted'] or cinfo['IsRestricted']:
                continue
            if 'Balance' not in info:
                continue
            binfo = info['Balance']
            #print(binfo)
            asset_name = binfo['Currency']
            balance = binfo['Balance']
            available = binfo['Available']
            pending = binfo['Pending']
            self.balances[asset_name] = {'balance': balance,
                                         'available': available }
            result[asset_name] = balance
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
