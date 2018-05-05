# handle multiple traders, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.strategy import *
from trader.TradePair import TradePair


#logger = logging.getLogger(__name__)

def split_symbol(symbol):
    base_name = None
    currency_name = None

    #if 'USDT' in symbol: return base_name, currency_name
    currencies = ['BTC', 'ETH', 'BNB', 'USDT']
    for currency in currencies:
        if symbol.endswith(currency):
            currency_name = currency
            base_name = symbol.replace(currency, '')
    return base_name, currency_name


class MultiTrader(object):
    def __init__(self, client, strategy_name='', assets_info=None, volumes=None,
                 account_name='Binance', simulate=False, accnt=None):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.simulate = simulate
        self.strategy_name = strategy_name
        if accnt:
            self.accnt = accnt
        else:
            self.accnt = AccountBinance(self.client, simulation=simulate)  # , account_name='Binance')
        self.assets_info = assets_info
        self.volumes = volumes

        if self.simulate:
            print("Running MultiTrader as simulation")

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
        #print("trade_pair {} added".format(symbol))

    def get_trader(self, symbol):
        if symbol not in self.trade_pairs.keys():
            self.add_trade_pair(symbol)
        return self.trade_pairs[symbol]

    def process_message(self, msg):
        if len(msg) == 0: return

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return
            #if len(msg) == 0: return

            #if msg['s'].endswith('USDT') and msg['s'] != 'BTCUSDT': return

            if msg['s'] not in self.trade_pairs.keys():
                self.add_trade_pair(msg['s'])

            if msg['s'] not in self.trade_pairs.keys(): return
            if self.volumes and msg['s'] not in self.volumes.keys(): return
            symbol_trader = self.trade_pairs[msg['s']]
            symbol_trader.run_update(msg)
            return

        for part in msg:
            if 's' not in part.keys(): continue
            #if len(self.trade_pairs) == 0: continue

            #if part['s'].endswith('USDT') and part['s'] != 'BTCUSDT': continue
            if part['s'] not in self.trade_pairs.keys():
                #print("adding {} to trade_pairs".format(part['s']))
                self.add_trade_pair(part['s'])

            if part['s'] not in self.trade_pairs.keys(): continue
            #if self.volumes and part['s'] not in self.volumes.keys(): continue
            symbol_trader = self.trade_pairs[part['s']]
            symbol_trader.run_update(part)
