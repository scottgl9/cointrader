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

class CurrencyBalanceHandler(object):
    def __init__(self, accnt=None):
        self.accnt = accnt
        self.currencies = {}
        for name in self.accnt.get_currencies():
            self.currencies[name] = { 'balance': 0.0 }

    def get_currencies(self):
        return self.currencies.keys()

    def is_zero_balance(self, name):
        balance = self.get_balance(name)
        if balance:
            return False
        return True

    def get_balance(self, name):
        if name not in self.currencies.keys():
            return 0
        return self.currencies[name]['balance']

    def set_balance(self, name, balance=0.0):
        if name not in self.currencies.keys():
            return False
        self.currencies[name]['balance'] = balance
        return True

    # note that amount = price * order_size, so amount can be specified instead of the former
    def update_for_asset_buy(self, base, currency, price=0, order_size=0, amount=0):
        if currency not in self.currencies.keys():
            return False
        if not amount:
            amount = self.accnt.round_quote_pair(base, currency, float(price * order_size))
        self.currencies[currency]['balance'] -= amount
        return True

    def update_for_asset_sell(self, base, currency, price=0, order_size=0, amount=0):
        if currency not in self.currencies.keys():
            return False
        if not amount:
            amount = self.accnt.round_quote_pair(base, currency, float(price * order_size))
        self.currencies[currency]['balance'] += amount
        return True
