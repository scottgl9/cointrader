# handle multiple traders, one for each base / currency we want to trade
from trader.account.AccountBinance import AccountBinance
from trader.RankManager import RankManager
from trader.strategy import *
from trader.TradePair import TradePair
from trader.indicator.SMA import SMA
from trader.lib.MessageHandler import Message, MessageHandler

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
                 account_name='Binance', simulate=False, accnt=None, ranking=True):
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
        self.rank = RankManager()
        self.ranking = ranking
        self.roc_ema = SMA(50)
        self.tickers = None
        self.msg_handler = MessageHandler()

        self.initial_btc = self.accnt.get_asset_balance(asset='BTC')['balance']

        if self.simulate:
            print("Running MultiTrader as simulation")

    def add_trade_pair(self, symbol):
        base_min_size = 0.0
        quote_increment = 0.0
        if symbol in self.assets_info.keys():
            base_min_size = float(self.assets_info[symbol]['minQty'])
            quote_increment = float(self.assets_info[symbol]['tickSize'])

        base_name, currency_name = split_symbol(symbol)
        if not base_name or not currency_name: return

        strategy = select_strategy(self.strategy_name,
                                   self.client,
                                   base_name,
                                   currency_name,
                                   account_handler=self.accnt,
                                   base_min_size=base_min_size,
                                   tick_size=quote_increment,
                                   rank=self.rank)

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
            #if self.volumes and msg['s'] not in self.volumes.keys(): return

            symbol_trader = self.trade_pairs[msg['s']]
            if self.ranking and symbol_trader.last_close != 0.0:
                close = float(msg['c'])
                roc = 100.0 * (close / symbol_trader.last_close - 1)
                self.rank.update(msg['s'], self.roc_ema.update(roc))
            symbol_trader.update_tickers(self.tickers)
            symbol_trader.run_update(msg)
        else:
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
                if self.ranking and symbol_trader.last_close != 0.0:
                    close = float(msg['c'])
                    roc = 100.0 * (close / symbol_trader.last_close - 1)
                    self.rank.update(msg['s'], self.roc_ema.update(roc))
                symbol_trader.update_tickers(self.tickers)
                symbol_trader.run_update(part)

        # handle incoming messages
        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages_by_dst_id(Message.ID_MULTI):
                if msg.cmd == Message.MSG_MARKET_BUY:
                    self.place_buy_order(msg.src_id, msg.price, msg.size)
                elif msg.cmd == Message.MSG_MARKET_SELL:
                    self.place_sell_order(msg.src_id, msg.price, msg.size, msg.buy_price)
                elif msg.cmd == Message.MSG_MARKET_SELL_ALL:
                    self.sell_all()
            self.msg_handler.clear()

    # sell off everything that was bought
    def sell_all(self):
        for trader in self.trade_pairs.values():
            buy_price = trader.strategy.buy_price
            buy_size = trader.strategy.buy_size
            ticker_id = trader.strategy.ticker_id
            if float(buy_price) == 0 or float(buy_size) == 0:
                continue
            self.place_sell_order(ticker_id, 0, buy_size, buy_price)
            trader.strategy.buy_price = 0.0
            trader.strategy.buy_size = 0.0
            trader.strategy.buy_order_id = None

    def place_buy_order(self, ticker_id, price, size):
        result = self.accnt.buy_market(size=size, price=price, ticker_id=ticker_id)
        if not self.accnt.simulate:
            print(result)

        print("buy({}, {}) @ {}".format(ticker_id, size, price))
        if not self.accnt.simulate and not result:
            return

        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            self.buy_order_id = None
            if not self.accnt.simulate:
                if 'orderId' not in result:
                    print("WARNING: orderId not found for {}".format(ticker_id))
                    return
                orderid = result['orderId']
                self.buy_order_id = orderid

        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def place_sell_order(self, ticker_id, price, size, buy_price):
        result = self.accnt.sell_market(size=size, price=price, ticker_id=ticker_id)
        if not self.accnt.simulate and not result: return
        if self.accnt.simulate or ('status' in result and result['status'] == 'FILLED'):
            pprofit = 100.0 * (price - buy_price) / buy_price
            if self.tickers:
                current_btc = self.accnt.get_total_btc_value(self.tickers)
                tpprofit = 100.0 * (current_btc - self.initial_btc) / self.initial_btc
                print("sell({}, {}) @ {} (bought @ {}, {}%)\t{}%".format(ticker_id,
                                                                         size,
                                                                         price,
                                                                         buy_price,
                                                                         round(pprofit, 2),
                                                                         round(tpprofit, 2)))
            else:
                print("sell({}, {}) @ {} (bought @ {}, {}%)".format(ticker_id,
                                                                    size,
                                                                    price,
                                                                    buy_price,
                                                                    round(pprofit, 2)))

            if not self.accnt.simulate:
                total_usd, total_btc = self.accnt.get_account_total_value()
                print("Total balance USD = {}, BTC={}".format(total_usd, total_btc))
        if not self.accnt.simulate:
            self.accnt.get_account_balances()

    def update_tickers(self, tickers):
        self.tickers = tickers
