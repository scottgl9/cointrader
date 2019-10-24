# base class for all strategies
import sys
import importlib
from datetime import datetime
from trader.lib.TraderMessageHandler import TraderMessageHandler
from trader.lib.SignalHandler import SignalHandler
from .TraderMessage import TraderMessage
from trader.KlinesDB import KlinesDB


# realtime hourly signals are used in conjunction with trade_mode = realtime
def select_rt_hourly_signal(sname, kdb, accnt, symbol, asset_info, exit_fail=True):
    signal = None
    try:
        # load realtime hourly signal dynamically using importlib
        mod = importlib.import_module("trader.signal.hourly.realtime.{}".format(sname))
        signal = getattr(mod, sname)
    except ImportError:
        if exit_fail:
            print("Unable to load realtime hourly signal {}".format(sname))
            sys.exit(-1)

    # if sname == 'RT_Hourly_EMA_Crossover':
    #     from trader.signal.hourly.realtime.RT_Hourly_EMA_Crossover import RT_Hourly_EMA_Crossover
    #     signal = RT_Hourly_EMA_Crossover
    # elif sname == 'RT_Hourly_LSMA_Crossover':
    #     from trader.signal.hourly.realtime.RT_Hourly_LSMA_Crossover import RT_Hourly_LSMA_Crossover
    #     signal = RT_Hourly_LSMA_Crossover
    # elif sname == 'RT_Hourly_LSTM_Signal':
    #     from trader.signal.hourly.realtime.RT_Hourly_LSTM_Signal import RT_Hourly_LSTM_Signal
    #     signal = RT_Hourly_LSTM_Signal
    # elif sname == 'RT_Hourly_MACD_Signal':
    #     from trader.signal.hourly.realtime.RT_Hourly_MACD_Signal import RT_Hourly_MACD_Signal
    #     signal = RT_Hourly_MACD_Signal
    # elif sname == 'RT_Hourly_MinMax_Signal':
    #     from trader.signal.hourly.realtime.RT_Hourly_MinMax_Signal import RT_Hourly_MinMax_Signal
    #     signal = RT_Hourly_MinMax_Signal
    # elif sname == 'RT_Hourly_ROC_Signal':
    #     from trader.signal.hourly.realtime.RT_Hourly_ROC_Signal import RT_Hourly_ROC_Signal
    #     signal = RT_Hourly_ROC_Signal
    # elif sname == "None":
    #     return None
    # elif exit_fail:
    #     print("Unable to load realtime hourly signal {}".format(sname))
    #     sys.exit(-1)

    if not signal:
        return None

    return signal(accnt, symbol, asset_info, kdb)


# realtime hourly signals are used in conjunction with trade_mode = hourly
def select_hourly_signal(sname, kdb, accnt, symbol, asset_info, exit_fail=True):
    signal = None
    if sname == 'Hourly_MACD_Signal':
        from trader.signal.hourly.Hourly_MACD_Signal import Hourly_MACD_Signal
        signal = Hourly_MACD_Signal
    elif sname == "None":
        return None
    elif exit_fail:
        print("Unable to load hourly signal {}".format(sname))
        sys.exit(-1)

    if not signal:
        return None

    return signal(accnt, symbol, asset_info, kdb)


class StrategyBase(object):
    # signal modes
    SIGNAL_MODE_HOURLY = 1
    SIGNAL_MODE_REALTIME = 2
    # single signal, single open buy per signal
    SINGLE_SIGNAL_SINGLE_ORDER = 1
    # multiple signals, single open buy per signal
    MULTI_SIGNAL_SINGLE_ORDER = 2
    # single signal, multiple open buy orders per signal
    SINGLE_SIGNAL_MULTI_ORDER = 3
    # multiple signals, multiple open buys per signal
    MULTI_SIGNAL_MULTI_ORDER = 4

    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 asset_info=None, config=None, logger=None):
        self.strategy_name = None
        self.realtime_signals_enabled = True

        # by default, only one executed buy order without matching sell order allowed for one signal
        self.order_method = StrategyBase.SINGLE_SIGNAL_SINGLE_ORDER
        self.logger = logger
        self.config = config
        self.tickers = None
        self.base = base
        self.currency = currency
        self.ticker_id = None
        self.asset_info = asset_info
        self.base_precision = 8
        self.quote_precision = 8
        self.min_qty = 0
        self.base_min_size = 0
        self.quote_increment = 0
        # disable ability to buy in a strategy based on filters
        self.filter_buy_disabled = False

        if self.asset_info:
            self.base_precision = self.asset_info.baseAssetPrecision
            self.quote_precision = self.asset_info.quotePrecision
            self.min_qty = float(self.asset_info.min_qty)
            self.base_min_size = float(self.asset_info.base_step_size)
            self.quote_increment = float(self.asset_info.currency_step_size)

        self.base_fmt = "{:." + str(self.base_precision) + "f}"
        self.quote_fmt = "{:." + str(self.quote_precision) + "f}"

        self.client = client
        self.accnt = account_handler
        self.order_handler = order_handler

        self.hourly_klines_disabled = False
        self.make_ticker_id()
        # true if base, and currency are both tradable currencies (ex ETH/BTC)
        self._currency_pair = self.accnt.is_currency_pair(base=self.base, currency=self.currency)

        self.msg_handler = TraderMessageHandler()
        self.signal_handler = SignalHandler(self.ticker_id, logger=logger)
        self.simulate = self.accnt.simulate
        self.trade_size_handler = None
        self.count_prices_added = 0
        self.kline = None
        self.hourly_update_fail_count = 0
        self.first_hourly_update_ts = 0
        self.last_hourly_update_ts = 0

        self.rt_hourly_klines = None
        self.rt_hourly_klines_signal = None
        self.rt_hourly_klines_handler = None
        self.rt_hourly_klines_processed = False
        self.rt_hourly_klines_loaded = False
        self.rt_hourly_klines_disabled = False
        self.rt_use_hourly_klines = False

        self.rt_max_hourly_model_count = 0
        self.rt_hourly_preload_hours = 0

        self.trader_mode_realtime = self.accnt.trade_mode_realtime()
        self.trader_mode_hourly = self.accnt.trade_mode_hourly()

        if self.accnt.trade_mode_realtime():
            self.rt_use_hourly_klines = self.config.get('rt_use_hourly_klines')
            self.rt_max_hourly_model_count = int(self.config.get('rt_max_hourly_model_count'))
            self.rt_hourly_preload_hours = int(self.config.get('rt_hourly_preload_hours'))

            if self.rt_use_hourly_klines:
                root_path = self.config.get('path')
                db_path = self.config.get('db_path')
                hourly_klines_db_file = self.config.get('hourly_kline_db_file')
                kdb_path = "{}/{}/{}".format(root_path, db_path, hourly_klines_db_file)
                try:
                    self.rt_hourly_klines_handler = KlinesDB(self.accnt,
                                                             kdb_path,
                                                             symbol=self.ticker_id,
                                                             logger=self.logger)
                    if not self.rt_hourly_klines_handler.symbol_in_table_list(self.ticker_id):
                        self.rt_hourly_klines_handler.close()
                        self.rt_hourly_klines_handler = None
                except IOError:
                    self.logger.warning("hourly_klines_handler: Failed to load {}".format(kdb_path))
                    self.rt_hourly_klines_handler = None

        self.tpprofit = 0
        self.last_tpprofit = 0
        self.start_ts = 0
        self.timestamp = 0
        self.last_timestamp = 0

        self.last_price = 0.0
        self.price = 0.0
        self.last_close = 0.0
        self.low = 0
        self.last_low = 0
        self.high = 0
        self.last_high = 0

        self.min_trade_size = 0.0
        self.min_trade_size_qty = 1.0
        self.min_price = 0.0
        self.max_price = 0.0

        # for more accurate simulation
        self.delayed_buy_msg = None
        self.delayed_sell_msg = None
        self.enable_buy = False
        self.disable_buy = False

        # buy information loaded from trade.db
        self.buy_loaded = False

    @staticmethod
    def select_signal_name(name, accnt=None, symbol=None, asset_info=None, kdb=None):
        signal = None
        # hourly rt signals
        signal = select_rt_hourly_signal(name, kdb, accnt, symbol, asset_info, exit_fail=False)
        if signal:
            return signal
        # hourly signals
        signal = select_hourly_signal(name, kdb, accnt, symbol, asset_info, exit_fail=False)
        if signal:
            return signal
        # realtime signals
        if name == "BTC_USDT_Signal":
            from trader.signal.global_signal.BTC_USDT_Signal import BTC_USDT_Signal
            signal = BTC_USDT_Signal
        elif name == "AEMA_Crossover_Test":
            from trader.signal.AEMA_Crossover_Test import AEMA_Crossover_Test
            signal = AEMA_Crossover_Test
        elif name == "Currency_Long_EMA":
            from trader.signal.long.Currency_Long_EMA import Currency_EMA_Long
            signal = Currency_EMA_Long
        elif name == "EMA_OBV_Crossover":
            from trader.signal.EMA_OBV_Crossover import EMA_OBV_Crossover
            signal = EMA_OBV_Crossover
        elif name == "Hybrid_Crossover_Test2":
            from trader.signal.Hybrid_Crossover_Test2 import Hybrid_Crossover_Test2
            signal = Hybrid_Crossover_Test2
        elif name == "MACD_Crossover":
            from trader.signal.MACD_Crossover import MACD_Crossover
            signal = MACD_Crossover
        elif name == "MTS_Crossover2_Signal":
            from trader.signal.MTS_Crossover2_Signal import MTS_Crossover2_Signal
            signal = MTS_Crossover2_Signal
        elif name == "MTS_SMA_Signal":
            from trader.signal.MTS_SMA_Signal import MTS_SMA_Signal
            signal = MTS_SMA_Signal
        elif name == "NULL_Signal":
            from trader.signal.NULL_Signal import NULL_Signal
            signal = NULL_Signal
        elif name == "RTKline_MACD_Cross_Signal":
            from trader.signal.RTKline_MACD_Cross_Signal import RTKline_MACD_Cross_Signal
            signal = RTKline_MACD_Cross_Signal
        else:
            print("Unable to load signal {}".format(name))
            sys.exit(-1)

        if signal:
            return signal(accnt, symbol, asset_info, kdb=kdb)

        return None

    def handle_msg_buy_complete(self, msg):
        return False

    def handle_msg_sell_complete(self, msg):
        return False

    def handle_msg_buy_failed(self, msg):
        return False

    def handle_msg_sell_failed(self, msg):
        return False

    def handle_msg_order_size_update(self, msg):
        return False

    # handle incoming messages from OrderHandler or MultiTrader
    def handle_incoming_messages(self):
        completed = False
        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages(src_id=TraderMessage.ID_MULTI, dst_id=self.ticker_id):
                if not msg:
                    continue
                if msg.is_read():
                    continue
                if msg.cmd == TraderMessage.MSG_BUY_COMPLETE:
                    if self.handle_msg_buy_complete(msg):
                        completed = True
                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_SELL_COMPLETE:
                    if self.handle_msg_sell_complete(msg):
                        completed = True
                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_BUY_FAILED:
                    if self.handle_msg_buy_failed(msg):
                        completed = True
                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_SELL_FAILED:
                    if self.handle_msg_sell_failed(msg):
                        completed = True
                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_ORDER_SIZE_UPDATE:
                    if self.handle_msg_order_size_update(msg):
                        completed = True
                    msg.mark_read()

            for msg in self.msg_handler.get_messages(src_id=TraderMessage.ID_ROOT, dst_id=self.ticker_id):
                if msg and msg.cmd == TraderMessage.MSG_BUY_UPDATE:
                    msg.mark_read()
            self.msg_handler.clear_read()

        return completed

    def get_ticker_id(self):
        return self.ticker_id

    def make_ticker_id(self):
        if self.accnt:
            self.ticker_id = self.accnt.make_ticker_id(self.base, self.currency)

    # true if base, and currency are both tradable currencies (ex ETH/BTC)
    def is_currency_pair(self):
        return self._currency_pair

    def get_signals(self):
        if self.signal_handler:
            return self.signal_handler.get_handlers()
        return None

    def round_base(self, price):
        if self.base_min_size != 0.0:
            return round(price, self.base_fmt.format(self.base_min_size).index('1') - 1)
        return price

    def round_quote(self, price):
        if self.quote_increment != 0.0:
            return round(price, self.quote_fmt.format(self.quote_increment).index('1') - 1)
        return price

    def round_quantity(self, size):
        if float(self.min_qty) != 0.0:
            precision = "{:.8f}".format(self.min_qty).index('1')
            if float(self.min_qty) < 1.0:
                precision -= 1
            return round(float(size), precision)
        return size

    # is_base == False: quote value, is_base == True: base value
    def my_float(self, value, is_base=True):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            if is_base:
                return self.base_fmt.format(float(value))
            return self.quote_fmt.format(float(value))

    def reset(self):
        pass

    def buy_signal(self, signal, price):
        pass

    def sell_signal(self, signal, price):
        pass

    def set_buy_price_size(self, buy_price, buy_size, sig_id=0):
        pass

    def run_update(self, kline):
        pass

    def run_update_signal(self, signal, price):
        pass

    def run_update_orderbook(self, msg):
        pass

    def update_total_percent_profit(self, tpprofit):
        self.last_tpprofit = self.tpprofit
        self.tpprofit = tpprofit
        self.signal_handler.update_total_percent_profit(tpprofit)

    def close(self):
        pass

    @staticmethod
    def datetime_to_float(d):
        epoch = datetime.utcfromtimestamp(0)
        total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
        # total_seconds will be in decimals (millisecond precision)
        return float(total_seconds)

    # compute if p1 is greater than p2 by X percent
    @staticmethod
    def percent_p1_gt_p2(p1, p2, percent):
        if p1 == 0: return False
        result = 100.0 * (float(p1) - float(p2)) / float(p1)
        if result <= percent:
            return False
        return True

    @staticmethod
    def percent_p2_gt_p1(p1, p2, percent):
        if p1 == 0: return False
        if p2 <= p1: return False
        result = 100.0 * (float(p2) - float(p1)) / float(p1)
        if result <= percent:
            return False
        return True

    # compute if p1 is less than p2 by X percent (p1 is "threshold")
    @staticmethod
    def percent_p1_lt_p2(p1, p2, percent):
        if p1 == 0: return False
        result = 100.0 * (float(p2) - float(p1)) / float(p1)
        if result >= percent:
            return False
        return True
