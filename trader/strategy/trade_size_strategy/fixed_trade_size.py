from trader.strategy.trade_size_strategy import trade_size_strategy_base


class fixed_trade_size(trade_size_strategy_base):
    def __init__(self, accnt, asset_info, trade_sizes=None):
        super(fixed_trade_size, self).__init__(accnt, asset_info)
        self.trade_sizes = trade_sizes
        try:
            if self.currency:
                self.trade_size = float(trade_sizes[self.currency])
            else:
                self.trade_size = 0
        except KeyError:
            self.trade_size = 0

    def check_buy_trade_size(self, price, size):
        if float(price) == 0 or float(size) == 0:
            return False

        if not self.currency:
            return False

        # if we have insufficient funds to buy
        available = float(self.accnt.get_asset_balance(self.currency)['available'])
        amount = self.round_quote(float(price) * float(size))

        if available <= amount:
            return False

        return True

    def compute_trade_size(self, price):
        trade_size = 0
        if not self.trade_size or not price:
            return trade_size
    
        trade_size = self.round_base(self.trade_size / price)

        #if self.accnt.is_currency_pair(base=self.base, currency=self.currency):
        #    trade_size = trade_size * self.multiplier

        trade_size = self.accnt.my_float(trade_size)

        return trade_size
