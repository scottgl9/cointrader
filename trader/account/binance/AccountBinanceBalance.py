from trader.account.AccountBaseBalance import AccountBaseBalance


class AccountBinanceBalance(AccountBaseBalance):
    def __init__(self, client, info, market, simulate=False, logger=None):
        self.client = client
        self.info = info
        self.market = market
        self.simulate = simulate
        self.logger = logger
        self.balances = {}

    def get_account_total_value(self, currency='USD', detailed=False):
        result = dict()
        result['assets'] = {}

        total_balance = 0.0

        for asset, value in self.get_account_balances(detailed=False).items():
            if float(value) == 0:
                continue
            if asset == currency:
                total_balance += value
                continue
            elif currency != 'USDT' and asset == 'USDT':
                symbol = self.info.make_ticker_id(currency, asset)
                price = float(self.market.get_ticker(symbol))
                if price:
                    total_balance += value / price
                elif self.simulate:
                    return 0.0
                continue
            symbol = self.info.make_ticker_id(asset, currency)
            price = float(self.market.get_ticker(symbol))
            #print(asset, value, price)
            if self.simulate and not price:
                return 0.0
            elif not price:
                continue
            total_balance += value * price

        return total_balance

    def get_account_balances(self, detailed=False):
        result = {}
        if not self.simulate:
            self.balances = {}
            for funds in self.client.get_account()['balances']:
                funds_free = float(funds['free'])
                funds_locked = float(funds['locked'])
                if funds_free == 0.0 and funds_locked == 0.0: continue
                asset_name = funds['asset']
                self.balances[asset_name] = {'balance': (funds_free + funds_locked), 'available': funds_free}
                result[asset_name] = funds_free + funds_locked
            if detailed:
                return self.balances
        else:
            if detailed:
                return self.balances
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
