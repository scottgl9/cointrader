from trader.account.CryptoAccountBaseBalance import CryptoAccountBaseBalance
from coinbase.rest import RESTBase, RESTClient

class AccountCoinbaseBalance(CryptoAccountBaseBalance):
    def __init__(self, client: RESTClient, info, market, simulate=False, logger=None):
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
            elif currency == 'USDC' and asset == 'USD':
                total_balance += value
                continue
            elif currency == 'USD' and asset == 'USDC':
                total_balance += value
                continue
            elif currency != 'USDC' and asset == 'USDC':
                symbol = self.info.make_ticker_id(currency, asset)
                price = float(self.market.get_ticker(symbol))
                if price:
                    total_balance += value / price
                elif self.simulate:
                    return 0.0
                continue
            elif currency != 'USD' and asset == 'USD':
                symbol = self.info.make_ticker_id(currency, asset)
                price = float(self.market.get_ticker(symbol))
                if price:
                    total_balance += value / price
                elif self.simulate:
                    return 0.0
                continue
            symbol = self.info.make_ticker_id(asset, currency)
            price = float(self.market.get_ticker(symbol))
            if not price and currency == 'USD':
                symbol = self.info.make_ticker_id(asset, 'USDC')
                price = float(self.market.get_ticker(symbol))
            elif not price and currency == 'USDC':
                symbol = self.info.make_ticker_id(asset, 'USD')
                price = float(self.market.get_ticker(symbol))
            if self.simulate and not price:
                return 0.0
            elif not price:
                continue
            total_balance += value * price

        return total_balance


    # implemented for CoinBase Pro
    def get_account_balances(self, detailed=False):
        if not self.simulate:
            self.balances = {}
            result = {}
            print(self.client.get_accounts())
            accounts = self.client.get_accounts().accounts
            print(self.client.get_portfolios())
            #print(self.client.get_portfolio_breakdown())
            #print(self.client.get_payment_method('USD'))
            print(self.client.get_portfolios("DEFAULT").portfolios)
            #print(self.client.get_portfolio_breakdown("DEFAULT").breakdown)
            print(self.client.get_futures_balance_summary())

            for account in accounts:
                asset_name = account.currency
                available_balance = 0.0
                hold_balance = 0.0

                if asset_name != account.hold['currency']:
                    print("Error: asset_name != account.hold.currency")
                if asset_name != account.available_balance['currency']:
                    print("Error: asset_name != account.available_balance.currency")

                # skip assets which are not available
                if not account.ready or not account.active:
                    continue

                # skip non-crypto assets
                #if account.type != 'ACCOUNT_TYPE_CRYPTO':
                #    continue

                available_balance = float(account.available_balance['value'])
                hold_balance = float(account.hold['value'])
                total_balance = available_balance + hold_balance
                
                self.balances[asset_name] = { 'total': total_balance,
                                              'available': available_balance,
                                              'hold': hold_balance}

                result[asset_name] = total_balance

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
