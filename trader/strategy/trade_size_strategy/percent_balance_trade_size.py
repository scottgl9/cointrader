# Buy / sell in a fixed percent amount of available currency(s)
from trader.strategy.trade_size_strategy import trade_size_strategy_base


class percent_balance_trade_size(trade_size_strategy_base):
    def __init__(self, accnt, asset_info, percent=5.0, multiplier=2):
        super(percent_balance_trade_size, self).__init__(accnt, asset_info)
        # currency pair symbol multiplier
        self.multiplier = multiplier
        self.percent = percent
        self._fraction = self.percent / 100.0
        self.available = float(self.accnt.get_asset_balance(self.currency)['available'])
        self.amount = 0
        if self.available * self._fraction > self.asset_info.min_qty:
            self.amount = self.available * self._fraction

    def check_buy_trade_size(self, price, size):
        if float(price) == 0 or float(size) == 0:
            return False

        # if we have insufficient funds to buy
        available = float(self.accnt.get_asset_balance(self.currency)['available'])

        # take into account price may increase during market buy
        price = float(price) + self.base_step_size

        amount = self.round_quote(float(price) * float(size))

        if available <= amount:
            return False

        return True

    def compute_trade_size(self, price):
        trade_size = 0
        if not self.amount:
            self.available = float(self.accnt.get_asset_balance(self.currency)['available'])
            if self.available * self._fraction > float(self.asset_info.min_qty):
                self.amount = self.round_quote(self.available * self._fraction)
            else:
                return trade_size
        else:
            trade_size = self.round_base(self.amount / float(price))

        if self.accnt.is_currency_pair(base=self.base, currency=self.currency):
            trade_size = trade_size * self.multiplier

        trade_size = self.my_float(trade_size)

        return trade_size
