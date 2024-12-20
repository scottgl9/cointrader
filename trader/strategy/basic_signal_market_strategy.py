from trader.lib.struct.TraderMessage import TraderMessage
from trader.strategy.trade_size.fixed_trade_size import fixed_trade_size
from trader.lib.struct.StrategyBase import StrategyBase, select_rt_hourly_signal
from trader.lib.struct.SignalBase import SignalBase
from trader.KlinesDB import KlinesDB


class basic_signal_market_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 config=None, asset_info=None, logger=None):
        super(basic_signal_market_strategy, self).__init__(client,
                                                           base,
                                                           currency,
                                                           account_handler,
                                                           order_handler,
                                                           asset_info,
                                                           config,
                                                           logger)
        self.strategy_name = 'basic_signal_market_strategy'

        self.min_percent_profit = float(self.config.get('min_percent_profit'))

        # get trade_sizes from config
        trade_sizes = config.get_section_field_options(field='trade_size')
        self.trade_size_handler = fixed_trade_size(self.accnt, asset_info, trade_sizes)

        signal_names = [self.config.get('signals')]

        for name in signal_names:
            signal = StrategyBase.select_signal_name(name,
                                                     self.accnt,
                                                     self.ticker_id,
                                                     asset_info,
                                                     kdb=None)
            self.signal_handler.add(signal)

    # clear pending sell trades which have been bought
    def reset(self, buy_price=0, buy_size=0):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = buy_price
            signal.buy_size = buy_size
            signal.buy_order_id = None

    def close(self):
        pass

    def buy_signal(self, signal, price):
        # wait until initial currency determined before placing buy order
        if self.accnt.simulate and self.accnt.initial_currency == 0:
            return False

        # don't buy a currency pair
        if self.accnt.is_currency_pair(self.ticker_id):
            return False

        # buy signal disabled by filter
        if self.filter_buy_disabled:
            return False

        try:
            if self.accnt.trades_disabled():
                return False

            if self.accnt.sell_only():
                return False
        except AttributeError:
            pass

        if float(signal.buy_price) != 0.0 or self.disable_buy:
            return False

        # limit number of market buy orders without corresponding market sell orders
        try:
            max_market_buy = self.accnt.max_market_buy()
        except AttributeError:
            max_market_buy = 0

        if max_market_buy != 0 and self.order_handler.open_market_buy_count >= max_market_buy:
            return False

        self.min_trade_size = self.trade_size_handler.compute_trade_size(price)
        if not self.trade_size_handler.check_buy_trade_size(price, self.min_trade_size):
            return False

        if self.last_close == 0:
            return False

        if signal.buy_signal():
            return True

        return False


    def sell_signal(self, signal, price):
        try:
            if self.accnt.trades_disabled():
                return False
        except AttributeError:
            pass

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

        if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, self.min_percent_profit):
            return False

        # if it's been over 8 hours since buy executed for symbol, sell as soon as percent profit > 0
        if (self.timestamp - signal.last_buy_ts) > self.accnt.hours_to_ts(8):
            return True

        # if buying is disabled and symbol is >= 1.0 percent profit, then sell
        if self.disable_buy:
            return True

        # if buy price was loaded from trade.db, don't wait for signal to sell
        if self.buy_loaded:
            return True

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
        signal.buy_price = buy_price
        signal.buy_size = buy_size
        self.buy_loaded = True
        self.logger.info("loading into {} price={} size={} sigid={}".format(self.ticker_id, buy_price, buy_size, sig_id))


    # handle received buy complete message from OrderHandler
    def handle_msg_buy_complete(self, msg):
        if not self.simulate:
            self.logger.info("BUY_COMPLETE for {} price={} size={}".format(msg.dst_id,
                                                                           msg.price,
                                                                           msg.size))
        signal = self.signal_handler.get_handler(id=msg.sig_id)
        if signal:
            signal.buy_size = msg.size
            signal.buy_price = msg.price
            signal.buy_timestamp = self.timestamp
            signal.last_buy_ts = self.timestamp
        else:
            self.logger.warning("BUY_COMPLETE failed, no signal for {}".format(msg.dst_id))

        return True

    # handle received sell complete message from OrderHandler
    def handle_msg_sell_complete(self, msg):
        if not self.simulate:
            self.logger.info("SELL_COMPLETE for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                         msg.price,
                                                                                         msg.buy_price,
                                                                                         msg.size))

        if self.min_trade_size_qty != 1.0:
            self.min_trade_size_qty = 1.0

        signal = self.signal_handler.get_handler(id=msg.sig_id)

        if signal:
            signal.last_sell_price = msg.price
            signal.last_buy_price = msg.buy_price
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.last_sell_price = msg.price
            signal.buy_timestamp = 0
            signal.prev_last_sell_ts = signal.last_sell_ts
            signal.last_sell_ts = self.timestamp
        else:
            self.logger.warning("SELL_COMPLETE failed, no signal for {}".format(msg.dst_id))

        # if buy price was loaded from trade.db, mark buy_loaded as fail since it was sold
        self.buy_loaded = False
        return True

    # handle received buy failed message from OrderHandler
    def handle_msg_buy_failed(self, msg):
        self.logger.info("BUY_FAILED for {} price={} size={} round_base={} round_quote={}".format(msg.dst_id,
                                                                                                  msg.price,
                                                                                                  msg.size,
                                                                                                  self.round_base(
                                                                                                  float(msg.size)),
                                                                                                  self.round_quote(
                                                                                                  float(msg.size))))
        if self.min_trade_size_qty != 1.0:
            self.min_trade_size_qty = 1.0
        signal = self.signal_handler.get_handler(id=msg.sig_id)
        if signal:
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_timestamp = 0
            # for failed buy, disable buys for this symbol for 4 hours
            signal.disabled = True
            signal.disabled_end_ts = signal.timestamp + self.accnt.hours_to_ts(4)
        else:
            self.logger.warning("BUY_FAILED failed, no signal for {}".format(msg.dst_id))
        msg.mark_read()
        return False

    # handle received sell failed message from OrderHandler
    def handle_msg_sell_failed(self, msg):
        self.logger.info("SELL_FAILED for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                   msg.price,
                                                                                   msg.buy_price,
                                                                                   msg.size))
        signal = self.signal_handler.get_handler(id=msg.sig_id)
        if signal:
            signal.buy_price = signal.last_buy_price
        else:
            self.logger.warning("SELL_FAILED failed, no signal for {}".format(msg.dst_id))
        msg.mark_read()
        return False

    # handle received order size update message from OrderHandler
    def handle_msg_order_size_update(self, msg):
        id = msg.sig_id
        signal = self.signal_handler.get_handler(id=id)
        self.logger.info("ORDER_SIZE_UPDATE for {} orig_size={} new_size={}".format(msg.dst_id,
                                                                                    signal.buy_size,
                                                                                    msg.size))
        signal.buy_size = msg.size
        return False

    def run_update(self, msg):
        return self.run_update_feed1(msg.kline)

    def run_update_feed1(self, kline):
        self.timestamp = kline.ts
        close = kline.close
        volume = kline.volume

        if not close or not volume:
            return

        if self.timestamp == self.last_timestamp:
            return

        self.signal_handler.pre_update(kline=kline)

        completed = self.handle_incoming_messages()

        for signal in self.signal_handler.get_handlers():
            self.run_update_signal(signal, close, signal_completed=completed)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close
        self.last_low = self.low
        self.last_high = self.high

    def run_update_signal(self, signal, price, signal_completed=False):
        # handle delayed buy/sell message
        if self.accnt.simulate and self.delayed_buy_msg and self.delayed_buy_msg.sig_id == signal.id:
            signal.buy_price = price
            self.delayed_buy_msg.price = signal.buy_price
            self.msg_handler.add(self.delayed_buy_msg)
            self.delayed_buy_msg = None

        if self.accnt.simulate and self.delayed_sell_msg and self.delayed_sell_msg.sig_id == signal.id:
            self.delayed_sell_msg.price = price
            signal.buy_price = 0
            signal.buy_size = 0
            self.msg_handler.add(self.delayed_sell_msg)
            self.delayed_sell_msg = None

        # prevent buying at the same price with the same timestamp with more than one signal
        if self.signal_handler.is_duplicate_buy(price, self.timestamp):
            return

        if not signal_completed and self.buy_signal(signal, price):
            self.buy_market(signal, price)

        if not signal_completed and self.sell_signal(signal, price):
            self.sell_market(signal, price)


    def buy_market(self, signal, price):
        if float(signal.buy_price) != 0:
            return

        if 'e' in str(self.min_trade_size):
            self.signal_handler.clear_handler_signaled()
            return

        # don't re-buy less than 60 minutes after a sell
        if signal.last_sell_ts != 0 and (self.timestamp - signal.last_sell_ts) < self.accnt.hours_to_ts(1):
            return

        # don't re-buy less than 60 minutes after start of sell
        if signal.last_start_sell_ts != 0 and (self.timestamp - signal.last_start_sell_ts) < self.accnt.hours_to_ts(1):
            return

        min_trade_size = self.min_trade_size

        if self.min_trade_size_qty != 1.0:
            min_trade_size = float(min_trade_size) * self.min_trade_size_qty

        signal.buy_size = min_trade_size

        if not float(signal.buy_size):
            return

        signal.buy_price = price

        # for more accurate simulation, delay buy message for one cycle in order to have the buy price
        # be the value immediately following the price that the buy signal was triggered
        if self.accnt.simulate and not self.delayed_buy_msg:
            self.delayed_buy_msg = TraderMessage(self.ticker_id,
                                                 TraderMessage.ID_MULTI,
                                                 TraderMessage.MSG_MARKET_BUY,
                                                 signal.id,
                                                 price,
                                                 signal.buy_size,
                                                 asset_info=self.asset_info,
                                                 buy_type=signal.buy_type)
        else:
            self.msg_handler.buy_market(self.ticker_id, signal.buy_price, signal.buy_size,
                                        sig_id=signal.id, asset_info=self.asset_info, buy_type=signal.buy_type)


    def sell_market(self, signal, price):
        if float(signal.buy_price) == 0:
            return

        sell_price = price

        # track ts for start of sell order
        signal.last_start_sell_ts = self.timestamp

        # for more accurate simulation, delay sell message for one cycle in order to have the buy price
        # be the value immediately following the price that the buy signal was triggered
        if self.accnt.simulate and not self.delayed_sell_msg:
            self.delayed_sell_msg = TraderMessage(self.ticker_id,
                                                  TraderMessage.ID_MULTI,
                                                  TraderMessage.MSG_MARKET_SELL,
                                                  signal.id,
                                                  sell_price,
                                                  signal.buy_size,
                                                  signal.buy_price,
                                                  asset_info=self.asset_info,
                                                  sell_type=signal.sell_type)
        else:
            self.msg_handler.sell_market(self.ticker_id, sell_price, signal.buy_size, signal.buy_price,
                                         sig_id=signal.id, asset_info=self.asset_info, sell_type=signal.sell_type)
