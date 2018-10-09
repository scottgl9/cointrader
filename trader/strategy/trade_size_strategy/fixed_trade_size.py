from trader.strategy.trade_size_strategy import trade_size_strategy_base

class fixed_trade_size(trade_size_strategy_base):
    def __init__(self, base, currency, base_min_size, tick_size, btc=0, eth=0, bnb=0, usdt=0):
        super(fixed_trade_size, self).__init__(base, currency, base_min_size, tick_size)
        self.usdt_trade_size = usdt
        self.btc_trade_size = btc
        self.eth_trade_size = eth
        self.bnb_trade_size = bnb

    def compute_trade_size(self, price):
        trade_size = 0
        if self.currency == 'BTC':
            trade_size = self.round_base(self.btc_trade_size / price)
            if self.base == 'ETH' or self.base == 'BNB':
                trade_size = self.my_float(trade_size * 3)
            else:
                trade_size = self.my_float(trade_size * 3)
        elif self.currency == 'ETH':
            trade_size = self.round_base(self.eth_trade_size / price)
            if self.base == 'BNB':
                trade_size = self.my_float(trade_size * 3)
            else:
                trade_size = self.my_float(trade_size * 3)
        elif self.currency == 'BNB':
            trade_size = self.round_base(self.bnb_trade_size / price)
            trade_size = self.my_float(trade_size)
        elif self.currency == 'USDT':
            trade_size = self.round_base(self.usdt_trade_size / price)
            trade_size = self.my_float(trade_size)

        return trade_size
