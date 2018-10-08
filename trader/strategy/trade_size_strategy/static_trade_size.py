from trader.strategy.trade_size_strategy import trade_size_strategy_base

class static_trade_size(trade_size_strategy_base):
    def __init__(self, base, currency, base_min_size=0.0, tick_size=0.0):
        super(static_trade_size, self).__init__(base, currency, base_min_size, tick_size)
        self.btc_trade_size = 0.0011
        self.eth_trade_size = 0.011
        self.bnb_trade_size = 0.8
        self.usdt_trade_size = 10.0

    def compute_trade_size(self, price):
        trade_size = 0
        if self.currency == 'BTC':
            trade_size = self.round_base(self.btc_trade_size / price)
            if trade_size != 0.0:
                if self.base == 'ETH' or self.base == 'BNB':
                    trade_size = self.my_float(trade_size * 3)
                else:
                    trade_size = self.my_float(trade_size * 3)
        elif self.currency == 'ETH':
            trade_size = self.round_base(self.eth_trade_size / price)
            if trade_size != 0.0:
                if self.base == 'BNB':
                    trade_size = self.my_float(trade_size * 3)
                else:
                    trade_size = self.my_float(trade_size * 3)
        elif self.currency == 'BNB':
            trade_size = self.round_base(self.bnb_trade_size / price)
            if trade_size != 0.0:
                trade_size = self.my_float(trade_size)
        elif self.currency == 'USDT':
            trade_size = self.round_base(self.usdt_trade_size / price)
            if trade_size != 0.0:
                trade_size = self.my_float(trade_size)

        return trade_size
