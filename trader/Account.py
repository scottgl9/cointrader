from trader.AccountBase import AccountBase
from trader.AccountGDAX import AccountGDAX

class Account(AccountBase):
    def __init__(self, auth_client, base_name, currency_name, account_name='GDAX'):
        if account_name is 'GDAX':
            self.auth_client = auth_client
            self.accnt = AccountGDAX(self.auth_client, base_name, currency_name)
