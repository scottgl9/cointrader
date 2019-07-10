from trader.lib.struct.Message import Message
from trader.strategy.trade_size_strategy.fixed_trade_size import fixed_trade_size
from trader.lib.struct.StrategyBase import StrategyBase, select_hourly_signal
from trader.lib.struct.SignalBase import SignalBase


class basic_signal_market_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', account_handler=None, order_handler=None,
                 config=None, asset_info=None, base_min_size=0.0, tick_size=0.0, logger=None):
        super(basic_signal_market_strategy, self).__init__(client,
                                                           base,
                                                           currency,
                                                           account_handler,
                                                           order_handler,
                                                           base_min_size,
                                                           tick_size,
                                                           asset_info,
                                                           config,
                                                           logger)
        self.strategy_name = 'hybrid_signal_market_strategy'

        self.min_percent_profit = float(self.config.get('min_percent_profit'))

        # set signal modes from config
        self.realtime_signals_enabled = False
        self.hourly_signals_enabled = False
        self.signal_modes = []
        signal_modes = self.config.get('signal_modes').split(',')
        for mode in signal_modes:
            if mode == 'realtime':
                self.realtime_signals_enabled = True
                self.signal_modes.append(StrategyBase.SIGNAL_MODE_REALTIME)
            elif mode == 'hourly':
                self.hourly_signals_enabled = True
                self.signal_modes.append(StrategyBase.SIGNAL_MODE_HOURLY)

        signal_names = [self.config.get('signals')]
        hourly_signal_name = self.config.get('hourly_signal')
        self.use_hourly_klines = self.config.get('use_hourly_klines')
        self.max_hourly_model_count = int(self.config.get('max_hourly_model_count'))
        self.hourly_preload_hours = int(self.config.get('hourly_preload_hours'))

        btc_trade_size = float(self.config.get('btc_trade_size'))
        eth_trade_size = float(self.config.get('eth_trade_size'))
        bnb_trade_size = float(self.config.get('bnb_trade_size'))
        pax_trade_size = float(self.config.get('pax_trade_size'))
        usdt_trade_size = float(self.config.get('usdt_trade_size'))
        trade_size_multiplier = float(self.config.get('trade_size_multiplier'))

        self.trade_size_handler = fixed_trade_size(self.accnt,
                                                   asset_info,
                                                   btc=btc_trade_size,
                                                   eth=eth_trade_size,
                                                   bnb=bnb_trade_size,
                                                   pax=pax_trade_size,
                                                   usdt=usdt_trade_size,
                                                   multiplier=trade_size_multiplier)

        if self.hourly_signals_enabled and self.use_hourly_klines and self.hourly_klines_handler and hourly_signal_name:
            self.hourly_klines_signal = select_hourly_signal(hourly_signal_name,
                                                             hkdb=self.hourly_klines_handler,
                                                             accnt=self.accnt,
                                                             symbol=self.ticker_id,
                                                             asset_info=self.asset_info)
        else:
            self.hourly_klines_signal = None


        if signal_names:
            for name in signal_names:
                if name == "BTC_USDT_Signal" and self.ticker_id != 'BTCUSDT':
                    continue
                signal = StrategyBase.select_signal_name(name,
                                                         self.accnt,
                                                         self.ticker_id,
                                                         asset_info,
                                                         hkdb=self.hourly_klines_handler)

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
                                                                    asset_info,
                                                                    hkdb=self.hourly_klines_handler))


    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None


    def buy_signal(self, signal, price):
        if self.accnt.trades_disabled():
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

        # don't buy if use_hourly_klines is True, and hourly klines aren't being used
        if self.use_hourly_klines:
            if not self.hourly_klines_handler or self.hourly_klines_disabled:
                return False

        if self.use_hourly_klines:
            if self.realtime_signals_enabled and self.hourly_klines_signal:
                if not self.hourly_klines_signal.hourly_buy_enable():
                    return False
            if self.hourly_signals_enabled and signal.hourly_buy_signal():
                return True

        if self.realtime_signals_enabled and signal.buy_signal():
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

        # if buy price was loaded from trade.db, don't wait for signal to sell
        if self.buy_loaded:
            return True

        if self.use_hourly_klines:
            if self.realtime_signals_enabled and self.hourly_klines_signal:
                if not self.hourly_klines_signal.hourly_sell_enable():
                    return False
            if self.hourly_signals_enabled and signal.hourly_sell_signal():
                return True

        if self.realtime_signals_enabled and signal.sell_signal():
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
            for msg in self.msg_handler.get_messages(src_id=Message.ID_MULTI, dst_id=self.ticker_id):
                if not msg:
                    continue
                if msg.is_read():
                    continue
                if msg.cmd == Message.MSG_BUY_COMPLETE:
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

                    msg.mark_read()
                    completed = True
                elif msg.cmd == Message.MSG_SELL_COMPLETE:
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

                    msg.mark_read()
                    completed = True
                elif msg.cmd == Message.MSG_BUY_FAILED:
                    self.logger.info("BUY_FAILED for {} price={} size={} round_base={} round_quote={}".format(msg.dst_id,
                                                                                 msg.price,
                                                                                 msg.size,
                                                                                 self.round_base(float(msg.size)),
                                                                                 self.round_quote(float(msg.size))))
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
                elif msg.cmd == Message.MSG_SELL_FAILED:
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
                elif msg.cmd == Message.MSG_ORDER_SIZE_UPDATE:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    self.logger.info("ORDER_SIZE_UPDATE for {} orig_size={} new_size={}".format(msg.dst_id,
                                                                                        signal.buy_size,
                                                                                        msg.size))
                    signal.buy_size = msg.size
                    msg.mark_read()

            for msg in self.msg_handler.get_messages(src_id=Message.ID_ROOT, dst_id=self.ticker_id):
                if msg and msg.cmd == Message.MSG_BUY_UPDATE:
                    msg.mark_read()
            self.msg_handler.clear_read()

        return completed


    def load_hourly_klines(self, ts):
        if self.ticker_id not in self.hourly_klines_handler.table_symbols:
            self.hourly_klines_disabled = True
            return

        # end_ts is first hourly ts for simulation
        hourly_ts = self.accnt.get_hourly_ts(ts)
        self.hourly_klines_signal.hourly_load(hourly_ts, self.hourly_preload_hours, ts)
        if self.hourly_klines_signal.uses_models:
            self.accnt.loaded_model_count += 1


    def run_update(self, kline, cache_db=None):
        close = kline.close
        self.low = kline.low
        self.high = kline.high
        volume = kline.volume_quote

        if not self.timestamp:
            if self.hourly_signals_enabled and not self.hourly_klines_loaded:
                # set initial hourly update ts
                self.first_hourly_update_ts = self.accnt.get_hourly_ts(kline.ts)
                self.last_hourly_update_ts = self.first_hourly_update_ts
                # hourly klines with model loading
                if self.hourly_klines_signal and self.hourly_klines_signal.uses_models:
                    # limit maximum number of models to load, unless max_hourly_model_count is zero
                    if not self.max_hourly_model_count or self.accnt.loaded_model_count <= self.max_hourly_model_count:
                        self.load_hourly_klines(kline.ts)
                        self.hourly_klines_loaded = True
                    else:
                        self.hourly_klines_disabled = True
                else:
                    end_ts = self.accnt.get_hourly_ts(kline.ts)
                    start_ts = end_ts - self.accnt.hours_to_ts(self.hourly_preload_hours)
                    self.signal_handler.hourly_load(start_ts, end_ts, kline.ts)
                    if self.hourly_klines_signal:
                        self.load_hourly_klines(kline.ts)
                    self.hourly_klines_loaded = True

        self.timestamp = kline.ts

        if close == 0 or volume == 0:
            return

        if self.timestamp == self.last_timestamp:
            return

        if self.hourly_signals_enabled and self.hourly_klines_signal and not self.hourly_klines_disabled:
            # wait 1 hour + 2 minutes before doing an update
            if (kline.ts - self.last_hourly_update_ts) >= self.accnt.seconds_to_ts(3720):
                hourly_ts = self.accnt.get_hourly_ts(kline.ts)
                if hourly_ts != self.last_hourly_update_ts:
                    # handle hourly signal updates for standard signals
                    self.signal_handler.hourly_update(hourly_ts)
                    if not self.hourly_klines_signal.hourly_update(hourly_ts=hourly_ts):
                        # hourly kline update failed
                        self.hourly_update_fail_count += 1
                    else:
                        self.hourly_update_fail_count = 0
                        self.last_hourly_update_ts = hourly_ts

                    if self.hourly_update_fail_count == 5:
                        self.logger.info("Hourly update FAILED 5 times for {}".format(self.ticker_id))
                        self.hourly_klines_disabled = True

        # handle realtime signal updates
        if self.realtime_signals_enabled:
            self.signal_handler.pre_update(close=close, volume=kline.volume_quote, ts=self.timestamp, cache_db=cache_db)

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

        if not signal_completed and self.sell_signal(signal, price):
            self.sell_market(signal, price)


    def buy_market(self, signal, price):
        if float(signal.buy_price) != 0:
            return

        if 'e' in str(self.min_trade_size):
            self.signal_handler.clear_handler_signaled()
            return

        # don't re-buy less than 60 minutes after a sell
        if signal.last_sell_ts != 0 and (self.timestamp - signal.last_sell_ts) < 1000 * 3600:
            return

        # don't re-buy less than 60 minutes after start of sell
        if signal.last_start_sell_ts != 0 and (self.timestamp - signal.last_start_sell_ts) < 1000 * 3600:
            return

        min_trade_size = self.min_trade_size

        if self.min_trade_size_qty != 1.0:
            min_trade_size = float(min_trade_size) * self.min_trade_size_qty

        # fix rounding issues for BNB currency symbols
        if self.currency == 'BNB':
            signal.buy_size = self.round_quantity(min_trade_size)
        else:
            signal.buy_size = min_trade_size

        if not float(signal.buy_size):
            return

        signal.buy_price = price

        # for more accurate simulation, delay buy message for one cycle in order to have the buy price
        # be the value immediately following the price that the buy signal was triggered
        if self.accnt.simulate and not self.delayed_buy_msg:
            self.delayed_buy_msg = Message(self.ticker_id,
                                           Message.ID_MULTI,
                                           Message.MSG_MARKET_BUY,
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
            self.delayed_sell_msg = Message(self.ticker_id,
                                            Message.ID_MULTI,
                                            Message.MSG_MARKET_SELL,
                                            signal.id,
                                            sell_price,
                                            signal.buy_size,
                                            signal.buy_price,
                                            asset_info=self.asset_info,
                                            sell_type=signal.sell_type)
        else:
            self.msg_handler.sell_market(self.ticker_id, sell_price, signal.buy_size, signal.buy_price,
                                         sig_id=signal.id, asset_info=self.asset_info, sell_type=signal.sell_type)

