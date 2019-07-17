# base class for all strategies
from datetime import datetime
from trader.lib.MessageHandler import MessageHandler
from trader.lib.SignalHandler import SignalHandler
from trader.HourlyKlinesDB import HourlyKlinesDB

def select_hourly_signal(sname, hkdb, accnt, symbol, asset_info):
    signal = None
    if sname == 'Hourly_EMA_Crossover':
        from trader.signal.hourly.Hourly_EMA_Crossover import Hourly_EMA_Crossover
        signal = Hourly_EMA_Crossover
    elif sname == 'Hourly_LSMA_Crossover':
        from trader.signal.hourly.Hourly_LSMA_Crossover import Hourly_LSMA_Crossover
        signal = Hourly_LSMA_Crossover
    elif sname == 'Hourly_LSTM_Signal':
        from trader.signal.hourly.Hourly_LSTM_Signal import Hourly_LSTM_Signal
        signal = Hourly_LSTM_Signal
    elif sname == 'Hourly_MinMax_Signal':
        from trader.signal.hourly.Hourly_MinMax_Signal import Hourly_MinMax_Signal
        signal = Hourly_MinMax_Signal
    elif sname == 'Hourly_ROC_Signal':
        from trader.signal.hourly.Hourly_ROC_Signal import Hourly_ROC_Signal
        signal = Hourly_ROC_Signal
    elif sname == "None":
        return None

    if not signal:
        return None

    return signal(accnt, symbol, asset_info, hkdb)


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
        # default setting for signal_modes
        self.signal_modes = [StrategyBase.SIGNAL_MODE_REALTIME, StrategyBase.SIGNAL_MODE_HOURLY]
        self.realtime_signals_enabled = True
        self.hourly_signals_enabled = True

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

        self.msg_handler = MessageHandler()
        self.signal_handler = SignalHandler(self.ticker_id, logger=logger)
        self.simulate = self.accnt.simulate
        self.trade_size_handler = None
        self.count_prices_added = 0
        self.mm_enabled = False
        self.kline = None
        self.hourly_klines = None
        self.hourly_klines_handler = None
        self.hourly_update_fail_count = 0
        self.first_hourly_update_ts = 0
        self.last_hourly_update_ts = 0

        self.use_hourly_klines = self.config.get('use_hourly_klines')
        if self.use_hourly_klines:
            hourly_klines_db_file = self.config.get('hourly_kline_db_file')
            try:
                self.hourly_klines_handler = HourlyKlinesDB(self.accnt,
                                                            hourly_klines_db_file,
                                                            symbol=self.ticker_id,
                                                            logger=self.logger)
                if not self.hourly_klines_handler.symbol_in_table_list(self.ticker_id):
                    self.hourly_klines_handler.close()
                    self.hourly_klines_handler = None
            except IOError:
                self.logger.warning("hourly_klines_handler: Failed to load {}".format(hourly_klines_db_file))
                self.hourly_klines_handler = None

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
        self.hourly_klines_processed = False
        self.hourly_klines_loaded = False

    @staticmethod
    def select_signal_name(name, accnt=None, symbol=None, asset_info=None, hkdb=None):
        signal = None
        # hourly signals
        if name == 'Hourly_EMA_Crossover':
            from trader.signal.hourly.Hourly_EMA_Crossover import Hourly_EMA_Crossover
            signal = Hourly_EMA_Crossover
        elif name == 'Hourly_LSMA_Crossover':
            from trader.signal.hourly.Hourly_LSMA_Crossover import Hourly_LSMA_Crossover
            signal = Hourly_LSMA_Crossover
        elif name == 'Hourly_LSTM_Signal':
            from trader.signal.hourly.Hourly_LSTM_Signal import Hourly_LSTM_Signal
            signal = Hourly_LSTM_Signal
        elif name == 'Hourly_MinMax_Signal':
            from trader.signal.hourly.Hourly_MinMax_Signal import Hourly_MinMax_Signal
            signal = Hourly_MinMax_Signal
        elif name == 'Hourly_ROC_Signal':
            from trader.signal.hourly.Hourly_ROC_Signal import Hourly_ROC_Signal
            signal = Hourly_ROC_Signal
        # realtime signals
        elif name == "BTC_USDT_Signal":
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
        elif name == "Hybrid_Crossover_Test":
            from trader.signal.Hybrid_Crossover_Test import Hybrid_Crossover_Test
            signal = Hybrid_Crossover_Test
        elif name == "Hybrid_Crossover_Test2":
            from trader.signal.Hybrid_Crossover_Test2 import Hybrid_Crossover_Test2
            signal = Hybrid_Crossover_Test2
        elif name == "MACD_Crossover":
            from trader.signal.MACD_Crossover import MACD_Crossover
            signal = MACD_Crossover
        elif name == "MTS_Crossover2_Signal":
            from trader.signal.MTS_Crossover2_Signal import MTS_Crossover2_Signal
            signal = MTS_Crossover2_Signal
        elif name == "MTS_Crossover3_Signal":
            from trader.signal.MTS_Crossover3_Signal import MTS_Crossover3_Signal
            signal = MTS_Crossover3_Signal
        elif name == "MTS_CrossoverTracker_Signal":
            from trader.signal.MTS_CrossoverTracker_Signal import MTS_CrossoverTracker_Signal
            signal = MTS_CrossoverTracker_Signal
        elif name == "MTS_Retracement_Signal":
            from trader.signal.MTS_Retracement_Signal import MTS_Retracement_Signal
            signal = MTS_Retracement_Signal
        elif name == "MTS_SMA_Signal":
            from trader.signal.MTS_SMA_Signal import MTS_SMA_Signal
            signal = MTS_SMA_Signal
        elif name == "NULL_Signal":
            from trader.signal.NULL_Signal import NULL_Signal
            signal = NULL_Signal
        elif name == "PPO_OBV":
            from trader.signal.PPO_OBV import PPO_OBV
            signal = PPO_OBV
        elif name == "PMO_Crossover":
            from trader.signal.PMO_Crossover import PMO_Crossover
            signal = PMO_Crossover
        elif name == "TrendStateTrack_Signal":
            from trader.signal.TrendStateTrack_Signal import TrendStateTrack_Signal
            signal = TrendStateTrack_Signal
        elif name == "TSI_Signal":
            from trader.signal.TSI_Signal import TSI_Signal
            signal = TSI_Signal
        elif name == "TSV_Signal":
            from trader.signal.TSV_Signal import TSV_Signal
            signal = TSV_Signal

        if signal:
            return signal(accnt, symbol, asset_info, hkdb=hkdb)

        return None


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

    def run_update(self, kline, cache_db=None):
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
