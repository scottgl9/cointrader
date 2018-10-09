# handle multiple TraiePairs, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.OrderHandler import OrderHandler
from trader.strategy import *
from trader.TradePair import TradePair
from trader.lib.MessageHandler import Message, MessageHandler
from trader.strategy.global_strategy.global_obv_strategy import global_obv_strategy

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


# handle incoming websocket messages for all symbols, and create new tradepairs
# for those that do not yet exist
class MultiTrader(object):
    def __init__(self, client, strategy_name='', assets_info=None, volumes=None,
                 account_name='Binance', simulate=False, accnt=None, logger=None, global_en=True):
        self.trade_pairs = {}
        self.accounts = {}
        self.client = client
        self.simulate = simulate
        self.strategy_name = strategy_name
        if accnt:
            self.accnt = accnt
        else:
            self.accnt = AccountBinance(self.client, simulation=simulate, logger=logger)  # , account_name='Binance')
        self.assets_info = assets_info
        self.volumes = volumes
        self.tickers = None
        self.msg_handler = MessageHandler()
        self.logger = logger
        self.notify = None
        self.current_ts = 0
        self.last_ts = 0
        self.check_ts = 3600 * 1000 # 1 hour
        self.check_count = 0
        self.stopped = False
        self.running = True
        self.order_handler = OrderHandler(self.accnt, self.msg_handler, self.logger)

        self.global_strategy = None
        self.global_en = global_en
        if self.global_en:
            self.global_strategy = global_obv_strategy()

        if self.simulate:
            self.logger.info("Running MultiTrader as simulation with strategy {}".format(self.strategy_name))
        else:
            self.logger.info("Running MultiTrade live with strategy {}".format(self.strategy_name))


    # create new tradepair handler and select strategy
    def add_trade_pair(self, symbol):
        base_min_size = 0.0
        quote_increment = 0.0
        if symbol in self.assets_info.keys():
            base_min_size = float(self.assets_info[symbol]['minQty'])
            quote_increment = float(self.assets_info[symbol]['tickSize'])

        base_name, currency_name = split_symbol(symbol)
        if not base_name or not currency_name: return

        # if an asset has deposit disabled, means its probably suspended
        # or de-listed so DO NOT trade this coin
        if self.accnt.deposit_asset_disabled(base_name):
            return

        strategy = select_strategy(self.strategy_name,
                                   self.client,
                                   base_name,
                                   currency_name,
                                   account_handler=self.accnt,
                                   base_min_size=base_min_size,
                                   tick_size=quote_increment,
                                   logger=self.logger)

        trade_pair = TradePair(self.client, self.accnt, strategy, base_name, currency_name)
        self.trade_pairs[symbol] = trade_pair

        if self.order_handler.trader_db:
            self.order_handler.trade_db_load_symbol(symbol, trade_pair)


    def get_trader(self, symbol):
        if symbol not in self.trade_pairs.keys():
            self.add_trade_pair(symbol)
        return self.trade_pairs[symbol]


    def process_message(self, msg):
        if len(msg) == 0: return

        if not isinstance(msg, list):
            if 's' not in msg.keys(): return

            if msg['s'] not in self.trade_pairs.keys():
                self.add_trade_pair(msg['s'])

            if msg['s'] not in self.trade_pairs.keys(): return

            symbol_trader = self.trade_pairs[msg['s']]
            if 'E' in msg:
                self.current_ts = msg['E']
            symbol_trader.update_tickers(self.tickers)
            symbol_trader.run_update(msg)

            if self.global_strategy:
                self.global_strategy.run_update(msg)

            self.order_handler.process_limit_order(msg)
        else:
            for part in msg:
                if 's' not in part.keys(): continue

                if part['s'] not in self.trade_pairs.keys():
                    self.add_trade_pair(part['s'])

                if part['s'] not in self.trade_pairs.keys(): continue
                #if self.volumes and part['s'] not in self.volumes.keys(): continue

                symbol_trader = self.trade_pairs[part['s']]
                if 'E' in part:
                    self.current_ts = part['E']
                symbol_trader.update_tickers(self.tickers)
                symbol_trader.run_update(part)

                if self.global_strategy:
                    self.global_strategy.run_update(part)

                self.order_handler.process_limit_order(part)

        # print alive check message once every 4 hours
        if not self.accnt.simulate:
            if self.last_ts == 0 and self.current_ts != 0:
                self.last_ts = self.current_ts
            elif self.current_ts != 0:
                if (self.current_ts - self.last_ts) > self.check_ts:
                    balances = self.accnt.get_account_balances()
                    self.last_ts = self.current_ts
                    self.check_count += 1
                    if self.check_count > 4:
                        self.logger.info("MultiTrader still running...")
                        self.logger.info(balances)
                        self.check_count = 0


        # handle incoming messages
        self.order_handler.process_order_messages()


    def update_tickers(self, tickers):
        self.tickers = tickers
        if self.order_handler:
            self.order_handler.update_tickers(self.tickers)
