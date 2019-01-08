# The purpose of this class addresses the following example scenario:
# 1) buy signal ETHBTC, trader executes buy for 1 ETH for symbol ETHBTC
# 2) trader updates balance, now ETH available as currency for trading
# 3) buy signal BNBETH, trader executes buy for BNBETH for 1 BNB, ETH balance now 0.9 for example
# 4) sell signal ETHBTC. balance of ETH is 0.9, but trader expects balance of ETH to be 0.9, so trade fails
# This class addresses this issue with the following:
# - Initial ETH balance marked as zero regardless of actual ETH balance
# - on buy execution of ETHBTC, this class sets ETH balance as buy size for the trade
# - on buy execution of BNBETH, this class removes X amount from ETH balance for the trade size of BNB
# - if on sell execution of BNBETH, this class adds X amount of ETH balance for the amount of ETH BNB sold for

class TradeBalanceHandler(object):
    def __init__(self, accnt=None, logger=None):
        self.accnt = accnt
        self.logger = logger
        self.balances = {}

    def is_zero_balance(self, name):
        balance = self.get_balance(name)
        if balance:
            return False
        return True

    def get_balances(self):
        return self.balances

    def get_balance(self, name):
        try:
            balance = self.balances[name]['balance']
        except KeyError:
            return 0
        return balance

    def set_balance(self, name, balance=0.0):
        try:
            self.balances[name]['balance'] = float(balance)
        except KeyError:
            self.balances[name] = {'balance': float(balance)}

    def update_for_buy(self, price, size, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        if not self.is_zero_balance(currency):
            amount = self.accnt.round_quote_pair(base, currency, float(price) * float(size))
            self.balances[currency]['balance'] -= amount

        if not self.is_zero_balance(base):
            self.balances[base]['balance'] += float(size)
        else:
            self.set_balance(base, size)

        return True

    def update_for_sell(self, price, size, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        if not self.is_zero_balance(currency):
            amount = self.accnt.round_quote_pair(base, currency, float(price) * float(size))
            self.balances[currency]['balance'] += amount

        self.balances[base]['balance'] -= float(size)

        return True
