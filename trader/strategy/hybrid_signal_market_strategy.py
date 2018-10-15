from trader.lib.Message import Message
from trader.lib.MessageHandler import MessageHandler
from trader.strategy.trade_size_strategy.static_trade_size import static_trade_size
from trader.strategy.StrategyBase import StrategyBase
from trader.signal.SignalBase import SignalBase
from trader.signal import select_signal_name
from trader.indicator.OBV import OBV


class hybrid_signal_market_strategy(StrategyBase):
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
        super(hybrid_signal_market_strategy, self).__init__(client,
                                                            name,
                                                            currency,
                                                            account_handler,
                                                            base_min_size,
                                                            tick_size,
                                                            logger)
        self.strategy_name = 'hybrid_signal_market_strategy'
        self.last_price = self.price = 0.0
        self.last_close = 0.0
        self.low = 0
        self.last_low = 0
        self.high = 0
        self.last_high = 0

        self.signal_handler.add(select_signal_name("Hybrid_Crossover"))

        self.obv = OBV()

        self.timestamp = 0
        self.last_timestamp = 0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.last_50_prices = []
        self.prev_last_50_prices = []
        self.trend_upward_count = 0
        self.trend_downward_count = 0

        self.last_price = 0.0
        self.min_trade_size = 0.0 #self.base_min_size * 20.0
        self.min_trade_size_qty = 1.0
        self.min_price = 0.0
        self.max_price = 0.0
        self.trade_size_handler = static_trade_size(name, currency, base_min_size, tick_size, usdt=10)

    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None


    def buy_signal(self, signal, price):
        if float(signal.buy_price) != 0.0: return False

        # if more than 500 seconds between price updates, ignore signal
        if (self.timestamp - self.last_timestamp) > 500:
            return False

        # if we have insufficient funds to buy
        if self.accnt.simulate:
            balance_available = self.accnt.get_asset_balance_tuple(self.currency)[1]
            size = self.round_base(float(balance_available) / float(price))
        else:
            size=self.accnt.get_asset_balance(self.currency)['available']

        #self.min_trade_size = self.compute_min_trade_size(price)
        self.min_trade_size = self.trade_size_handler.compute_trade_size(price)

        if not self.trade_size_handler.check_buy_trade_size(size):
            return False

        if float(self.min_trade_size) == 0.0 or size < float(self.min_trade_size):
            return False

        if self.last_close == 0:
            return False

        # do not buy back in the previous buy/sell price range
        if signal.last_buy_price != 0 and signal.last_sell_price != 0:
            if signal.last_buy_price <= price <= signal.last_sell_price:
                return False

        if signal.buy_signal():
            return True

        return False


    def sell_signal(self, signal, price):
        if float(signal.buy_price) == 0.0 or float(signal.buy_size) == 0.0:
            return False

        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < float(self.min_trade_size) or balance_available == 0.0:
            return False

        if not self.accnt.simulate and signal.buy_order_id:
            if price > float(signal.buy_price):
                # assume that this is the actual price that the market order executed at
                print("Updated buy_price from {} to {}".format(signal.buy_price, price))
                signal.buy_price = price
                signal.buy_order_id = None
                return False

        if signal.sell_long_signal():
            if (price - signal.buy_price) / signal.buy_price <= -0.1:
                return True

        if price < float(signal.buy_price):
            return False

        if self.base == 'ETH' or self.base == 'BNB':
            if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
                return False
        else:
            if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
                return False

        if signal.sell_signal():
            return True

        return False


    def set_buy_price_size(self, buy_price, buy_size, sig_id=0):
        signal = self.signal_handler.get_handler(id=sig_id)
        if not signal:
            self.logger.info("set_buy_price(): sigid {} not in signal_handler for {}: price={}, size={}".format(sig_id,
                                                                                                                self.ticker_id,
                                                                                                                buy_price,
                                                                                                                buy_size))
            return
        #if signal.buy_price == 0 and signal.buy_size == 0:
        signal.buy_price = buy_price
        signal.buy_size = buy_size
        self.logger.info("loading into {} price={} size={} sigid={}".format(self.ticker_id, buy_price, buy_size, sig_id))


    # NOTE: low and high do not update for each kline with binance
    def run_update(self, kline):
        # HACK REMOVE THIS
        #if self.currency == 'USDT':
        #    return
        close = kline.close
        self.low = kline.low
        self.high = kline.high
        volume = kline.volume

        if close == 0 or volume == 0:
            return

        self.timestamp = kline.ts

        if self.timestamp == self.last_timestamp:
            return

        self.obv.update(close, volume)

        self.signal_handler.pre_update(close=close, volume=volume, ts=self.timestamp)

        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages(src_id=Message.ID_MULTI, dst_id=self.ticker_id):
                if msg and msg.cmd == Message.MSG_BUY_FAILED:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    self.logger.info("BUY_FAILED for {} price={} size={}".format(msg.dst_id,
                                                                                 msg.price,
                                                                                 msg.size))
                    if self.min_trade_size_qty != 1.0:
                        self.min_trade_size_qty = 1.0
                    signal.buy_price = 0.0
                    signal.buy_size = 0.0
                    signal.buy_timestamp = 0
                    msg.mark_read()
                elif msg and msg.cmd == Message.MSG_SELL_FAILED:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    self.logger.info("SELL_FAILED for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                               msg.price,
                                                                                               msg.buy_price,
                                                                                               msg.size))
                    signal.buy_price = signal.last_buy_price
                    msg.mark_read()

            for msg in self.msg_handler.get_messages(src_id=Message.ID_ROOT, dst_id=self.ticker_id):
                if msg and msg.cmd == Message.MSG_BUY_UPDATE:
                    msg.mark_read()
            self.msg_handler.clear_read()

        for signal in self.signal_handler.get_handlers():
            self.run_update_signal(signal, close)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close
        self.last_low = self.low
        self.last_high = self.high


    def run_update_signal(self, signal, price):
        # prevent buying at the same price with the same timestamp with more than one signal
        if self.signal_handler.is_duplicate_buy(price, self.timestamp):
            return

        if signal.get_flag() == SignalBase.FLAG_SELL_ALL:
            balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
            if balance_available != 0 and signal.sell_signal():
                self.msg_handler.sell_market(self.ticker_id, price, balance_available, price, sig_id=signal.id)

        if self.buy_signal(signal, price):
            if 'e' in str(self.min_trade_size):
                self.signal_handler.clear_handler_signaled()
                return

            min_trade_size = self.min_trade_size

            if self.min_trade_size_qty != 1.0:
                min_trade_size = float(min_trade_size) * self.min_trade_size_qty

            signal.buy_price = price
            signal.buy_size = min_trade_size
            signal.buy_timestamp = self.timestamp
            self.msg_handler.buy_market(self.ticker_id, price, signal.buy_size, sig_id=signal.id)

        if self.sell_signal(signal, price):
            self.msg_handler.sell_market(self.ticker_id, price, signal.buy_size, signal.buy_price, sig_id=signal.id)

            if self.min_trade_size_qty != 1.0:
                self.min_trade_size_qty = 1.0

            signal.last_buy_price = signal.buy_price
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.last_sell_price = price
            signal.buy_timestamp = 0

