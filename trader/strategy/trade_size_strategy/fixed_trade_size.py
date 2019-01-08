from trader.strategy.trade_size_strategy import trade_size_strategy_base

class fixed_trade_size(trade_size_strategy_base):
    def __init__(self, accnt, asset_info, btc=0, eth=0, bnb=0, pax=0, usdt=0, multiplier=2):
        super(fixed_trade_size, self).__init__(accnt, asset_info)
        # currency pair symbol multiplier
        self.multiplier = multiplier
        self.usdt_trade_size = usdt
        self.btc_trade_size = btc
        self.eth_trade_size = eth
        self.bnb_trade_size = bnb
        self.pax_trade_size = pax

    def check_buy_trade_size(self, size):
        if self.currency == 'BTC' and size < self.btc_trade_size:
            return False
        elif self.currency == 'ETH' and size < self.eth_trade_size:
            return False
        elif self.currency == 'BNB' and size < self.bnb_trade_size:
            return False
        elif self.currency == 'PAX' and size < self.usdt_trade_size:
            return False
        elif self.currency == 'USDT' and size < self.usdt_trade_size:
            return False

        return True

    def compute_trade_size(self, price):
        trade_size = 0
        if self.currency == 'BTC':
            trade_size = self.round_base(self.btc_trade_size / price)
        elif self.currency == 'ETH':
            trade_size = self.round_base(self.eth_trade_size / price)
        elif self.currency == 'BNB':
            trade_size = self.round_base(self.bnb_trade_size / price)
        elif self.currency == 'PAX':
            trade_size = self.round_base(self.pax_trade_size / price)
        elif self.currency == 'USDT':
            trade_size = self.round_base(self.usdt_trade_size / price)

        if self.accnt.is_currency_pair(base=self.base, currency=self.currency):
            trade_size = trade_size * self.multiplier

        trade_size = self.my_float(trade_size)

        return trade_size
