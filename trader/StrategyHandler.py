from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.account import gdax
from trader.strategy import select_strategy


class StrategyHandler(object):
    def __init__(self, client, strategy_name, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.strategy = select_strategy(strategy_name, client, name, currency, account_handler, order_handler)
        self.strategy_name = strategy_name
        self.client = client
        if not account_handler:
            self.accnt = AccountGDAX(self.client, name, currency)
        else:
            self.accnt = account_handler

        self.orderbook = OrderBookGDAX()
        #if not order_handler:
        self.order_handler = OrderHandler(self.accnt)
        self.pc = gdax.PublicClient()

        self.buy_signal_count = self.sell_signal_count = 0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.accnt.get_account_balance()
        self.accnt.update_24hr_stats()
        print("Started {} strategy".format(self.strategy_name))
        print("Account balance: {} USD - {} BTC".format(self.accnt.quote_currency_balance, self.accnt.balance))

    def get_ticker_id(self):
        return self.accnt.get_ticker_id()

    def html_run_stats(self):
        return self.strategy.html_run_stats()

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, price):
        self.update_last_50_prices(price)
        self.order_handler.update_market_price(price)
        self.order_handler.process_limit_orders(price)

        self.strategy.run_update_price(price)

    def run_update_orderbook(self, msg):
        self.strategy.run_update_orderbook(msg)

    def close(self):
        pass
