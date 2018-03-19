# handle multiple traders, one for each base / currency we want to trade
from trader.Account import Account
from trader.strategy import *


def split_symbol(symbol):
    base_name = None
    currency_name = None
    currencies = ['BTC', 'ETH', 'BNB']
    for currency in currencies:
        if symbol.endswith(currency):
            currency_name = currency
            base_name = symbol.replace(currency, '')
    return base_name, currency_name


class MultiTrader(object):
    def __init__(self, client, strategy_name='', symbols=None, account_name='Binance'):
        self.traders = {}
        self.accounts = {}
        for symbol in symbols:
            base_name, currency_name = split_symbol(symbol)
            accnt = Account(client, base_name, currency_name, account_name='Binance')
            trader = select_strategy(strategy_name, client, base_name, currency_name,
                                     account_handler=accnt, order_handler=None)

            if symbol not in self.accounts.keys():
                self.accounts[symbol] = accnt
                self.traders[symbol] = trader

    def process_message(self, msg):
        if 's' not in msg: return
        if msg['s'] not in self.accounts.keys(): return

        symbol_trader = self.traders[msg['s']]
        symbol_trader.run_update_price(float(msg['o']))
        symbol_trader.run_update_price(float(msg['c']))
