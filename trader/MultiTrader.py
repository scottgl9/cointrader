# handle multiple traders, one for each base / currency we want to trade
from trader.Account import Account
from trader.AccountBinance import AccountBinance
from trader.strategy import *
from trader.TradePair import TradePair

def split_symbol(symbol):
    base_name = None
    currency_name = None

    if 'USDT' in symbol: return base_name, currency_name
    currencies = ['BTC', 'ETH', 'BNB']
    for currency in currencies:
        if symbol.endswith(currency):
            currency_name = currency
            base_name = symbol.replace(currency, '')
    return base_name, currency_name


class MultiTrader(object):
    def __init__(self, client, strategy_name='', assets_info=None, volumes=None, account_name='Binance'):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.strategy_name = strategy_name
        self.accnt = AccountBinance(self.client)  # , account_name='Binance')
        self.assets_info = assets_info
        self.volumes = volumes

        #for symbol in symbols:
        #    base_name, currency_name = split_symbol(symbol)
        #    accnt = AccountBinance(client, base_name, currency_name) #, account_name='Binance')
        #    trader = select_strategy(strategy_name, client, base_name, currency_name,
        #                             account_handler=accnt)

    def add_trade_pair(self, symbol):
        base_min_size = 0.0
        quote_increment = 0.0
        if symbol in self.assets_info.keys():
            base_min_size = float(self.assets_info[symbol]['minQty'])
            quote_increment = float(self.assets_info[symbol]['tickSize'])

        base_name, currency_name = split_symbol(symbol)
        if not base_name or not currency_name: return

        strategy = select_strategy(self.strategy_name, self.client, base_name, currency_name,
                                   account_handler=self.accnt, base_min_size=base_min_size, tick_size=quote_increment)
        trade_pair = TradePair(self.client, self.accnt, strategy, base_name, currency_name)

        self.trade_pairs[symbol] = trade_pair

    def process_message(self, msg):
        if len(msg) == 0: return

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return
            #if len(msg) == 0: return

            if msg['s'].endswith('USDT'): return

            if msg['s'] not in self.trade_pairs.keys():
                #print("adding {} to trade_pairs".format(msg['s']))
                self.add_trade_pair(msg['s'])

            if msg['s'] not in self.trade_pairs.keys(): return
            #if msg['s'] not in self.volumes.keys(): return
            #print("process_message: symbol={} price={}".format(msg['s'], msg['o']))
            #print("process_message({})".format(msg))
            symbol_trader = self.trade_pairs[msg['s']]
            symbol_trader.run_update_price(float(msg['o']))
            symbol_trader.run_update_price(float(msg['c']))
            return

        for part in msg:
            if 's' not in part.keys(): continue
            #if len(self.trade_pairs) == 0: continue

            if part['s'].endswith('USDT'): return
            if part['s'] not in self.trade_pairs.keys():
                #print("adding {} to trade_pairs".format(part['s']))
                self.add_trade_pair(part['s'])

            if part['s'] not in self.trade_pairs.keys(): continue
            #if part['s'] not in self.volumes.keys(): continue
            #print("process_message: symbol={} price={}".format(msg['s'], msg['o']))
            #print("process_message({})".format(msg))
            symbol_trader = self.trade_pairs[part['s']]

            symbol_trader.run_update_price(float(part['o']))
            symbol_trader.run_update_price(float(part['c']))
