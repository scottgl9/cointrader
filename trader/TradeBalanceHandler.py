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
        self.currencies = {}
        for name in self.accnt.get_currencies():
            self.currencies[name] = { 'balance': 0.0 }
        self.currency_pair_symbols = self.accnt.get_currency_trade_pairs()
        self.currency_pairs = {}
        for symbol in self.currency_pair_symbols:
            self.currency_pairs[symbol] = {'size': 0.0 }

    def get_currencies(self):
        return self.currencies.keys()

    def is_zero_balance(self, name):
        balance = self.get_balance(name)
        if balance:
            return False
        return True

    def get_size(self, symbol):
        try:
            result = self.currency_pairs[symbol]['size']
        except KeyError:
            return 0
        return result

    def set_size(self, symbol, size=0):
        self.currency_pairs[symbol]['size'] = size

    def get_balance(self, name):
        if name not in self.currencies.keys():
            return 0
        return self.currencies[name]['balance']

    def set_balance(self, name, balance=0.0):
        if name not in self.currencies.keys():
            return False
        #self.logger.info("\tset_balance({}, {})".format(name, balance))
        self.currencies[name]['balance'] = balance
        return True

    def update_for_buy(self, symbol, price, size, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        if symbol not in self.currency_pair_symbols:
            return False
        self.currency_pairs[symbol]['balance'] -= size
        return True

    def update_for_sell(self, symbol, price, size, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        if symbol not in self.currency_pair_symbols:
            return False
        self.currency_pairs[symbol]['balance'] += size
        return True

    # note that amount = price * order_size, so amount can be specified instead of the former
    def update_for_asset_buy(self, price=0, order_size=0, amount=0, symbol=None, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        balance = self.accnt.round_quote_pair(base, currency, self.accnt.get_asset_balance(currency)['balance'])

        if currency not in self.currencies.keys():
            return False
        if not amount:
            amount = self.accnt.round_quote_pair(base, currency, float(price) * float(order_size))
        if self.logger:
            pre_amount = self.currencies[currency]['balance']
            post_amount = pre_amount - amount
            self.logger.info("\tbuy({}{}): {} {} {}".format(base, currency, currency, post_amount, balance))
        self.currencies[currency]['balance'] -= amount
        return True

    def update_for_asset_sell(self, price=0, order_size=0, amount=0, symbol=None, asset_info=None):
        base = asset_info.base
        currency = asset_info.currency

        balance = self.accnt.round_quote_pair(base, currency, self.accnt.get_asset_balance(currency)['balance'])

        if currency not in self.currencies.keys():
            return False
        if not amount:
            amount = self.accnt.round_quote_pair(base, currency, float(price) * float(order_size))
        #if amount < asset_info.min_price:
        #    return False
        if self.logger:
            pre_amount = self.currencies[currency]['balance']
            post_amount = pre_amount + amount
            self.logger.info("\tsell({}{}): {} {} {}".format(base, currency, currency, post_amount, balance))
        self.currencies[currency]['balance'] += amount
        return True
