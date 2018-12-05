from trader.lib.Message import Message
from trader.lib.MessageHandler import MessageHandler
from trader.strategy.trade_size_strategy.trade_size_strategy_base import trade_size_strategy_base
from trader.strategy.trade_size_strategy.static_trade_size import static_trade_size
from trader.strategy.StrategyBase import StrategyBase
from trader.signal.SignalBase import SignalBase
from trader.indicator.OBV import OBV

class hybrid_signal_market_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', signal_names=None, account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
        super(hybrid_signal_market_strategy, self).__init__(client,
                                                            base,
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

        if signal_names:
            for name in signal_names:
                signal = StrategyBase.select_signal_name(name)
                if signal.mm_enabled:
                    self.mm_enabled = True
                # don't add global signal if global_filter doesn't match ticker_id
                if signal.global_signal and signal.global_filter != self.ticker_id:
                    continue
                self.signal_handler.add(signal)
        else:
            self.signal_handler.add(StrategyBase.select_signal_name("Hybrid_Crossover"))

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
        self.trade_size_handler = static_trade_size(base, currency, base_min_size, tick_size, usdt=10)
        # for more accurate simulation
        self.delayed_buy_msg = None
        self.delayed_sell_msg = None
        self.update_buy_price = False
        self.update_sell_price = False
        self.enable_buy = False
        self.disable_buy = False

    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None


    def buy_signal(self, signal, price):
        if float(signal.buy_price) != 0.0:
            #if signal.buy_signal():
            #    signal.sell_marked = False
            return False

        # if more than 500 seconds between price updates, ignore signal
        if not self.mm_enabled and (self.timestamp - self.last_timestamp) > 1000 * 0.5:
            return False

        #if signal.sell_timestamp != 0 and (self.timestamp - signal.sell_timestamp) < 1000 * 60 * 60:
        #    return False

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
        #if signal.last_buy_price != 0 and signal.last_sell_price != 0:
        #    if signal.last_buy_price <= price <= signal.last_sell_price:
        #        return False

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

        if signal.sell_long_signal():
            return True

        if price < float(signal.buy_price):
            return False

        #if not signal.sell_marked and signal.sell_signal():
        #    signal.sell_marked = True

        if self.base == 'ETH' or self.base == 'BNB':
            if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
                return False
        else:
            if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
                return False

        #if signal.sell_marked:
        #    return True

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
    ## mmkline is kline from MarketManager which is filtered and resampled
    def run_update(self, kline, mmkline=None):
        # HACK REMOVE THIS
        #if self.currency == 'USDT':
        #    return
        if mmkline:
            close = mmkline.close
            self.low = mmkline.low
            self.high = mmkline.high
            volume = mmkline.volume
            self.timestamp = mmkline.ts
            self.kline = kline
        else:
            close = kline.close
            self.low = kline.low
            self.high = kline.high
            volume = kline.volume
            self.timestamp = kline.ts

        if close == 0 or volume == 0:
            return

        if self.timestamp == self.last_timestamp:
            return

        self.obv.update(close, volume)

        self.signal_handler.pre_update(close=close, volume=volume, ts=self.timestamp)

        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages(src_id=Message.ID_MULTI, dst_id=self.ticker_id):
                if msg and msg.cmd == Message.MSG_BUY_FAILED:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    if not self.accnt.simulate:
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
            # if total profit drops to less than -1.5%
            if signal.buy_price != 0 and self.tpprofit != self.last_tpprofit and self.tpprofit < -0.015:
                #print(self.tpprofit)
                # TODO: do something here if total profit below -1.5%
                self.sell(signal, kline.close)
            if signal.is_global() and signal.global_filter == kline.symbol:
                signal.pre_update(kline.close, kline.volume, kline.ts)
                if signal.enable_buy and not self.enable_buy:
                    self.msg_handler.buy_enable(self.ticker_id)
                elif signal.disable_buy and not self.disable_buy:
                    self.msg_handler.buy_disable(self.ticker_id)
                self.disable_buy = signal.disable_buy
                self.enable_buy = signal.enable_buy
            else:
                self.run_update_signal(signal, close)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close
        self.last_low = self.low
        self.last_high = self.high


    def run_update_signal(self, signal, price):
        # handle delayed buy/sell message
        if self.accnt.simulate and self.delayed_buy_msg and self.delayed_buy_msg.sig_id == signal.id:
            signal.buy_price = price
            self.delayed_buy_msg.price = signal.buy_price
            self.msg_handler.add(self.delayed_buy_msg)
            self.delayed_buy_msg = None

        if self.accnt.simulate and self.delayed_sell_msg and self.delayed_sell_msg.sig_id == signal.id:
            self.delayed_sell_msg.price = price
            self.msg_handler.add(self.delayed_sell_msg)
            self.delayed_sell_msg = None
            if self.min_trade_size_qty != 1.0:
                self.min_trade_size_qty = 1.0

            signal.last_buy_price = signal.buy_price
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.last_sell_price = price
            signal.buy_timestamp = 0

        # keep track of the highest close price after a buy
        if signal.buy_price_high != 0 and price > signal.buy_price_high:
            signal.buy_price_high = price

        if not self.accnt.simulate and self.update_buy_price and price > signal.buy_price:
            signal.buy_price = price
            self.update_buy_price = False
        elif not self.accnt.simulate and self.update_sell_price:
            signal.last_sell_price = price
            self.update_sell_price = False

        # prevent buying at the same price with the same timestamp with more than one signal
        if self.signal_handler.is_duplicate_buy(price, self.timestamp):
            return

        if signal.get_flag() == SignalBase.FLAG_SELL_ALL:
            balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
            if balance_available != 0 and signal.sell_signal():
                self.msg_handler.sell_market(self.ticker_id, price, balance_available, price, sig_id=signal.id)

        if self.buy_signal(signal, price):
            self.buy(signal, price)

        if self.sell_signal(signal, price):
            self.sell(signal, price)


    def buy(self, signal, price):
        if 'e' in str(self.min_trade_size):
            self.signal_handler.clear_handler_signaled()
            return

        min_trade_size = self.min_trade_size

        if self.min_trade_size_qty != 1.0:
            min_trade_size = float(min_trade_size) * self.min_trade_size_qty

        # if self.mm_enabled:
        #    signal.buy_price = self.kline.close
        # else:
        signal.buy_price = price
        signal.buy_size = min_trade_size
        signal.buy_timestamp = self.timestamp
        signal.last_buy_ts = self.timestamp
        signal.sell_timestamp = 0
        signal.buy_price_high = signal.buy_price

        # for more accurate simulation, delay buy message for one cycle in order to have the buy price
        # be the value immediately following the price that the buy signal was triggered
        if self.accnt.simulate and not self.delayed_buy_msg:
            self.delayed_buy_msg = Message(self.ticker_id,
                                           Message.ID_MULTI,
                                           Message.MSG_MARKET_BUY,
                                           signal.id,
                                           price,
                                           signal.buy_size)
        else:
            self.msg_handler.buy_market(self.ticker_id, signal.buy_price, signal.buy_size, sig_id=signal.id)
            # for trader running live. Delay setting buy_price until next price
            self.update_buy_price = True


    def sell(self, signal, price):
        # if self.mm_enabled:
        #    sell_price = self.kline.close
        # else:
        sell_price = price

        # for more accurate simulation, delay sell message for one cycle in order to have the buy price
        # be the value immediately following the price that the buy signal was triggered
        if self.accnt.simulate and not self.delayed_sell_msg:
            signal.buy_price_high = 0
            self.delayed_sell_msg = Message(self.ticker_id,
                                            Message.ID_MULTI,
                                            Message.MSG_MARKET_SELL,
                                            signal.id,
                                            sell_price,
                                            signal.buy_size,
                                            signal.buy_price)
        else:
            self.msg_handler.sell_market(self.ticker_id, sell_price, signal.buy_size, signal.buy_price,
                                         sig_id=signal.id)

            if self.min_trade_size_qty != 1.0:
                self.min_trade_size_qty = 1.0

            signal.last_buy_price = signal.buy_price
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.last_sell_price = sell_price
            signal.last_sell_ts = self.timestamp
            signal.buy_timestamp = 0
            signal.sell_timestamp = self.timestamp
            signal.buy_price_high = 0

            # for trader running live. Delay setting sell_price until next price
            self.update_sell_price = True
