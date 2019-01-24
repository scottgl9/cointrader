from trader.strategy.trade_size_strategy import trade_size_strategy_base


class static_trade_size(trade_size_strategy_base):
    def __init__(self, accnt, asset_info, btc=0, eth=0, bnb=0, usdt=0):
        super(static_trade_size, self).__init__(accnt, asset_info)
        self.usdt_trade_size = usdt
        self.btc_trade_size = 0
        self.eth_trade_size = 0
        self.bnb_trade_size = 0

    def check_buy_trade_size(self, price, size):
        if self.currency == 'BTC' and size < self.btc_trade_size:
            return False
        elif self.currency == 'ETH' and size < self.eth_trade_size:
            return False
        elif self.currency == 'BNB' and size < self.bnb_trade_size:
            return False
        elif self.currency == 'USDT' and size < self.usdt_trade_size:
            return False

        return True

    def compute_trade_size(self, price):
        trade_size = 0
        if float(self.btc_trade_size) == 0:
            if self.tickers and 'BTCUSDT' in self.tickers.keys():
                if isinstance(self.tickers['BTCUSDT'], float):
                    btc_usdt = float(self.tickers['BTCUSDT'])
                else:
                    btc_usdt = float(self.tickers['BTCUSDT'][4])
                #btc_usdt = float(self.tickers['BTCUSDT'])
                self.btc_trade_size = self.usdt_trade_size / btc_usdt
            else:
                self.btc_trade_size = 0.0011

        if float(self.eth_trade_size) == 0:
            if self.tickers and 'ETHUSDT' in self.tickers.keys():
                #eth_usdt = float(self.tickers['ETHUSDT'])
                if isinstance(self.tickers['ETHUSDT'], float):
                    eth_usdt = float(self.tickers['ETHUSDT'])
                else:
                    eth_usdt = float(self.tickers['ETHUSDT'][4])
                self.eth_trade_size = self.usdt_trade_size / eth_usdt
            else:
                self.eth_trade_size = 0.011
        if float(self.bnb_trade_size) == 0:
            if self.tickers and 'BNBSDT' in self.tickers.keys():
                #bnb_usdt = float(self.tickers['BNBUSDT'])
                if isinstance(self.tickers['BNBUSDT'], float):
                    bnb_usdt = float(self.tickers['BNBUSDT'])
                else:
                    bnb_usdt = float(self.tickers['BNBUSDT'][4])
                self.bnb_trade_size = self.usdt_trade_size / bnb_usdt
            else:
                self.bnb_trade_size = 1.0

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
