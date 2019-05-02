# base class for all strategies
from datetime import datetime
from trader.lib.MessageHandler import Message, MessageHandler


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
    elif sname == 'Hourly_ROC_Signal':
        from trader.signal.hourly.Hourly_ROC_Signal import Hourly_ROC_Signal
        signal = Hourly_ROC_Signal
    if not signal:
        return None

    return signal(hkdb, accnt, symbol, asset_info)


class StrategyBase(object):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 hourly_klines_handler=None, base_min_size=0.0, tick_size=0.0, asset_info=None, config=None, logger=None):
        self.strategy_name = None
        self.logger = logger
        self.config = config
        self.tickers = None
        self.base = base
        self.currency = currency
        self.ticker_id = None
        self.asset_info = asset_info
        self.base_precision = 8
        self.quote_precision = 8

        if self.asset_info:
            self.base_precision = self.asset_info.baseAssetPrecision
            self.quote_precision = self.asset_info.quotePrecision

        self.base_fmt = "{:." + str(self.base_precision) + "f}"
        self.quote_fmt = "{:." + str(self.quote_precision) + "f}"

        self.base_min_size = float(base_min_size)
        self.quote_increment = float(tick_size)
        self.client = client
        self.accnt = account_handler
        self.order_handler = order_handler
        self.hourly_klines_handler = hourly_klines_handler
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
    def select_signal_name(name, accnt=None, symbol=None, asset_info=None):
        if name == "BTC_USDT_Signal":
            from trader.signal.global_signal.BTC_USDT_Signal import BTC_USDT_Signal
            return BTC_USDT_Signal(accnt)
        elif name == "AEMA_Crossover_Test":
            from trader.signal.AEMA_Crossover_Test import AEMA_Crossover_Test
            return AEMA_Crossover_Test(accnt, symbol, asset_info)
        elif name == "Currency_Long_EMA":
            from trader.signal.long.Currency_Long_EMA import Currency_EMA_Long
            return Currency_EMA_Long(accnt)
        elif name == "EFI_Breakout_Signal":
            from trader.signal.EFI_Breakout_Signal import EFI_Breakout_Signal
            return EFI_Breakout_Signal(accnt, symbol)
        elif name == "EMA_OBV_Crossover":
            from trader.signal.EMA_OBV_Crossover import EMA_OBV_Crossover
            return EMA_OBV_Crossover(accnt, symbol)
        elif name == "Hybrid_Crossover_Test":
            from trader.signal.Hybrid_Crossover_Test import Hybrid_Crossover_Test
            return Hybrid_Crossover_Test(accnt, symbol, asset_info)
        elif name == "Hybrid_Crossover_Test2":
            from trader.signal.Hybrid_Crossover_Test2 import Hybrid_Crossover_Test2
            return Hybrid_Crossover_Test2(accnt, symbol, asset_info)
        elif name == "KST_Crossover":
            from trader.signal.KST_Crossover import KST_Crossover
            return KST_Crossover(accnt, symbol)
        elif name == "MACD_Crossover":
            from trader.signal.MACD_Crossover import MACD_Crossover
            return MACD_Crossover(accnt, symbol)
        elif name == "PPO_OBV":
            from trader.signal.PPO_OBV import PPO_OBV
            return PPO_OBV(accnt, symbol)
        elif name == "PMO_Crossover":
            from trader.signal.PMO_Crossover import PMO_Crossover
            return PMO_Crossover(accnt, symbol)
        elif name == "TrendStateTrack_Signal":
            from trader.signal.TrendStateTrack_Signal import TrendStateTrack_Signal
            return TrendStateTrack_Signal(accnt, symbol, asset_info)
        elif name == "TSI_Signal":
            from trader.signal.TSI_Signal import TSI_Signal
            return TSI_Signal(accnt, symbol)
        elif name == "TSV_Signal":
            from trader.signal.TSV_Signal import TSV_Signal
            return TSV_Signal(accnt, symbol)

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

    ## mmkline is kline from MarketManager which is filtered and resampled
    def run_update(self, kline, mmkline=None, cache_db=None):
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
