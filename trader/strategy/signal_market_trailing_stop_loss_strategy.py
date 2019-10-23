from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.strategy.trade_size.fixed_trade_size import fixed_trade_size
from trader.lib.struct.StrategyBase import StrategyBase
from trader.lib.struct.SignalBase import SignalBase


class signal_market_trailing_stop_loss_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 config=None, asset_info=None, logger=None):
        super(signal_market_trailing_stop_loss_strategy, self).__init__(client,
                                                                        base,
                                                                        currency,
                                                                        account_handler,
                                                                        order_handler,
                                                                        asset_info,
                                                                        config,
                                                                        logger)
        self.strategy_name = 'signal_market_trailing_stop_loss_strategy'

        self.min_percent_profit = float(self.config.get('min_percent_profit'))

        # get trade_sizes from config
        trade_sizes = config.get_section_field_options(field='trade_size')
        self.trade_size_handler = fixed_trade_size(self.accnt, asset_info, trade_sizes)

        signal_names = [self.config.get('rt_signals')]
        hourly_signal_name = self.config.get('rt_hourly_signal')

        if signal_names:
            for name in signal_names:
                if name == "BTC_USDT_Signal" and self.ticker_id != 'BTCUSDT':
                    continue
                signal = StrategyBase.select_signal_name(name, self.accnt, self.ticker_id, asset_info)
                if signal.mm_enabled:
                    self.mm_enabled = True
                # don't add global signal if global_filter doesn't match ticker_id
                if signal.global_signal and signal.global_filter != self.ticker_id:
                    continue
                if not signal.global_signal and self.ticker_id.endswith('USDT'):
                    continue
                self.signal_handler.add(signal)
        else:
            self.signal_handler.add(StrategyBase.select_signal_name("Hybrid_Crossover",
                                                                    self.accnt,
                                                                    self.ticker_id,
                                                                    asset_info))

        # stop loss specific
        self.stop_loss_set = False
        self.stop_loss_price = 0
        self.next_stop_loss_price = 0
        self.prev_stop_loss_price = 0


    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None


    def buy_signal(self, signal, price):
        if self.accnt.trades_disabled():
            return False

        if self.is_currency_pair():
            return False

        if self.accnt.sell_only():
            return False

        if float(signal.buy_price) != 0.0 or self.disable_buy:
            return False

        # limit number of market buy orders without corresponding market sell orders
        max_market_buy = self.accnt.max_market_buy()
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
        if self.accnt.trades_disabled():
            return False

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

        # if buy price was loaded from trade.db, don't want for signal to sell
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
        #if signal.buy_price == 0 and signal.buy_size == 0:
        signal.buy_price = buy_price
        signal.buy_size = buy_size
        self.buy_loaded = True
        self.logger.info("loading into {} price={} size={} sigid={}".format(self.ticker_id, buy_price, buy_size, sig_id))


    def handle_incoming_messages(self):
        completed = False

        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages(src_id=TraderMessage.ID_MULTI, dst_id=self.ticker_id):
                if not msg:
                    continue
                if msg.is_read():
                    continue
                if msg.cmd == TraderMessage.MSG_BUY_COMPLETE:
                    if not self.simulate:
                        msg_type = TraderMessage.get_msg_type_string(msg.order_type)
                        self.logger.info("BUY_COMPLETE for {} price={} size={} type={}".format(msg.dst_id,
                                                                                               msg.price,
                                                                                               msg.size,
                                                                                               msg_type))
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    signal.buy_size = msg.size
                    signal.buy_price = msg.price
                    signal.buy_timestamp = self.timestamp
                    signal.last_buy_ts = self.timestamp

                    # set stop loss 2% under buy price
                    #if not self.stop_loss_set and not self.stop_loss_price:
                    #    self.stop_loss_price = self.round_base(0.98 * msg.price)
                    #    self.next_stop_loss_price = msg.price
                    #    self.set_sell_stop_loss(signal, self.stop_loss_price)

                    msg.mark_read()
                    completed = True
                elif msg.cmd == TraderMessage.MSG_SELL_COMPLETE:
                    if not self.simulate:
                        msg_type = TraderMessage.get_msg_type_string(msg.order_type)
                        self.logger.info("SELL_COMPLETE for {} price={} buy_price={} size={} type={}".format(msg.dst_id,
                                                                                                             msg.price,
                                                                                                             msg.buy_price,
                                                                                                             msg.size,
                                                                                                             msg_type))
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    signal.last_sell_price = msg.price
                    if msg.order_type == Order.TYPE_MARKET:
                        self.cancel_sell_stop_loss(signal)

                    if self.min_trade_size_qty != 1.0:
                        self.min_trade_size_qty = 1.0

                    signal.last_buy_price = msg.buy_price
                    signal.buy_price = 0.0
                    signal.buy_size = 0.0
                    signal.last_sell_price = msg.price
                    signal.buy_timestamp = 0
                    signal.last_sell_ts = self.timestamp

                    self.stop_loss_set = False
                    self.stop_loss_price = 0
                    self.next_stop_loss_price = 0

                    # if buy price was loaded from trade.db, mark buy_loaded as fail since it was sold
                    self.buy_loaded = False

                    msg.mark_read()
                    completed = True
                elif msg.cmd == TraderMessage.MSG_BUY_FAILED:
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    msg_type = TraderMessage.get_msg_type_string(msg.order_type)
                    self.logger.info("BUY_FAILED for {} price={} size={} type={}".format(msg.dst_id,
                                                                                         msg.price,
                                                                                         msg.size,
                                                                                         msg_type))
                    if self.min_trade_size_qty != 1.0:
                        self.min_trade_size_qty = 1.0
                    signal.buy_price = 0.0
                    signal.buy_size = 0.0
                    signal.buy_timestamp = 0
                    # for failed buy, disable buys for this symbol for 4 hours
                    signal.disabled = True
                    signal.disabled_end_ts = signal.timestamp + self.accnt.hours_to_ts(4)
                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_SELL_FAILED:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    msg_type = TraderMessage.get_msg_type_string(msg.order_type)
                    balance = str(self.accnt.get_asset_balance_tuple(self.base))
                    self.logger.info("SELL_FAILED for {} price={} buy_price={} size={} type={} balance={}".format(msg.dst_id,
                                                                                                                  msg.price,
                                                                                                                  msg.buy_price,
                                                                                                                  msg.size,
                                                                                                                  msg_type,
                                                                                                                  balance))
                    signal.buy_price = signal.last_buy_price
                    if self.stop_loss_set:
                        self.cancel_sell_stop_loss(signal)
                        self.stop_loss_set = False
                        self.stop_loss_price = 0
                        self.next_stop_loss_price = 0

                    msg.mark_read()
                elif msg.cmd == TraderMessage.MSG_ORDER_SIZE_UPDATE:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    self.logger.info("ORDER_SIZE_UPDATE for {} orig_size={} new_size={}".format(msg.dst_id,
                                                                                        signal.buy_size,
                                                                                        msg.size))
                    signal.buy_size = msg.size
                    msg.mark_read()

            for msg in self.msg_handler.get_messages(src_id=TraderMessage.ID_ROOT, dst_id=self.ticker_id):
                if msg and msg.cmd == TraderMessage.MSG_BUY_UPDATE:
                    msg.mark_read()
            self.msg_handler.clear_read()

        return completed


    def run_update(self, kline):
        if self.is_currency_pair():
            return False

        close = kline.close
        self.low = kline.low
        self.high = kline.high
        volume = kline.volume_quote

        if not self.timestamp:
            pass

        self.timestamp = kline.ts

        if close == 0 or volume == 0:
            return

        if self.timestamp == self.last_timestamp:
            return

        self.signal_handler.pre_update(close=close, volume=kline.volume_quote, ts=self.timestamp)

        completed = self.handle_incoming_messages()

        for signal in self.signal_handler.get_handlers():
            if signal.is_global() and signal.global_filter == kline.symbol:
                signal.pre_update(kline.close, kline.volume, kline.ts)
                if signal.enable_buy and not self.enable_buy:
                    self.msg_handler.buy_enable(self.ticker_id)
                elif signal.disable_buy and not self.disable_buy:
                    self.msg_handler.buy_disable(self.ticker_id)
                self.disable_buy = signal.disable_buy
                self.enable_buy = signal.enable_buy
            else:
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
            return

        if not signal_completed and self.sell_signal(signal, price):
            if self.stop_loss_set:
                self.cancel_sell_stop_loss(signal)
                self.stop_loss_price = 0
                self.next_stop_loss_price = 0

            self.sell_market(signal, price)
            return

        if signal.buy_price == 0 or signal.buy_size == 0:
            return

        balance = self.accnt.get_asset_balance_tuple(self.base)
        if float(balance[0]) == 0 or float(balance[1]) == 0:
            return

        if self.accnt.test_stop_loss() and (self.timestamp - signal.last_buy_ts) < self.accnt.seconds_to_ts(60):
            return

        if self.accnt.test_stop_loss() and not self.stop_loss_set and not self.next_stop_loss_price:
            if 0.98 * signal.buy_price < price < signal.buy_price:
                    self.stop_loss_price = self.round_quote(0.98 * signal.buy_price)
                    self.set_sell_stop_loss(signal, self.stop_loss_price)
                    self.next_stop_loss_price = signal.buy_price
            elif price > 1.01 * signal.buy_price:
                self.stop_loss_price = signal.buy_price
                self.set_sell_stop_loss(signal, self.stop_loss_price)
                self.next_stop_loss_price = signal.buy_price

        if not self.stop_loss_set and not self.accnt.test_stop_loss():
            if not self.stop_loss_price:
                self.stop_loss_price = signal.buy_price
            if StrategyBase.percent_p2_gt_p1(self.stop_loss_price, price, 2.0):
                self.set_sell_stop_loss(signal, self.stop_loss_price)
                self.next_stop_loss_price = price
        elif self.next_stop_loss_price and StrategyBase.percent_p2_gt_p1(self.next_stop_loss_price, price, 2.0):
            self.cancel_sell_stop_loss(signal)
            self.stop_loss_price = self.next_stop_loss_price
            self.set_sell_stop_loss(signal, self.stop_loss_price)
            self.next_stop_loss_price = price


    def set_sell_stop_loss(self, signal, price):
        if self.stop_loss_set:
            return False
        #self.logger.info("set_sell_stop_loss({}, {}, {})".format(self.ticker_id, price, signal.buy_size))
        sell_price = self.my_float(price)
        self.msg_handler.sell_stop_loss(self.ticker_id, sell_price, signal.buy_size, signal.buy_price, signal.id)
        self.stop_loss_set = True
        return True


    # instant cancel of sell order using order_handler directly
    def cancel_sell_stop_loss(self, signal):
        if not self.stop_loss_set:
            return False
        #self.logger.info("cancel_sell_stop_loss({})".format(self.ticker_id))
        self.order_handler.cancel_sell_order(self.ticker_id)
        self.stop_loss_set = False
        return True


    def buy_market(self, signal, price):
        if float(signal.buy_price) != 0:
            return

        if 'e' in str(self.min_trade_size):
            self.signal_handler.clear_handler_signaled()
            return

        min_trade_size = self.min_trade_size

        if self.min_trade_size_qty != 1.0:
            min_trade_size = float(min_trade_size) * self.min_trade_size_qty

        signal.buy_price = price
        signal.buy_size = min_trade_size

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
