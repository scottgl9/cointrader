from trader.AccountBase import AccountBase
from trader.AccountGDAX import AccountGDAX
from trader.AccountBinance import AccountBinance

class Account(object):
    def __init__(self, client, base_name, currency_name, account_name='GDAX'):
        self.accnt = None
        self.account_name = account_name
        if account_name is 'GDAX':
            self.client = client
            self.accnt = AccountGDAX(self.client, base_name, currency_name)
        elif account_name is 'Binance':
            self.client = client
            self.accnt = AccountBinance(self.client, base_name, currency_name)

    def get_account(self):
        return self.accnt

    def get_client(self):
        return self.client

    def get_account_name(self):
        return self.account_name
