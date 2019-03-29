from trader.lib.Message import Message
from trader.lib.MessageHandler import MessageHandler
from trader.strategy.trade_size_strategy.static_trade_size import static_trade_size
from trader.strategy.trade_size_strategy.fixed_trade_size import fixed_trade_size
from trader.strategy.trade_size_strategy.percent_balance_trade_size import percent_balance_trade_size
from trader.strategy.StrategyBase import StrategyBase
from trader.signal.SignalBase import SignalBase
from trader.indicator.OBV import OBV
from trader.indicator.EMA import EMA

class signal_market_trailing_stop_loss_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', signal_names=None, account_handler=None,
                 order_handler=None, asset_info=None, base_min_size=0.0, tick_size=0.0, logger=None):
        super(signal_market_trailing_stop_loss_strategy, self).__init__(client,
                                                            base,
                                                            currency,
                                                            account_handler,
                                                            order_handler,
                                                            base_min_size,
                                                            tick_size,
                                                            logger)
        self.strategy_name = 'signal_market_trailing_stop_loss_strategy'
        self.last_price = self.price = 0.0
        self.last_close = 0.0
        self.low = 0
        self.last_low = 0
        self.high = 0
        self.last_high = 0

        #signal_names.append("BTC_USDT_Signal")

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
        self.min_trade_size = 0.0
        self.min_trade_size_qty = 1.0
        self.min_price = 0.0
        self.max_price = 0.0
        self.asset_info = asset_info
        self.trade_size_handler = fixed_trade_size(self.accnt,
                                                   asset_info,
                                                   btc=0.004,
                                                   eth=0.1,
                                                   bnb=3,
                                                   pax=10.0,
                                                   usdt=10.0,
                                                   multiplier=5.0)
        #self.trade_size_handler = percent_balance_trade_size(self.accnt,
        #                                                     asset_info,
        #                                                     percent=10.0,
        #                                                     multiplier=5)

        # for more accurate simulation
        self.delayed_buy_msg = None
        self.delayed_sell_msg = None
        self.update_buy_price = False
        self.update_sell_price = False
        self.enable_buy = False
        self.disable_buy = False
        self.simulate = self.accnt.simulate

        # stop loss specific
        self.stop_loss_set = False
        self.stop_loss_price = 0
        self.next_stop_loss_price = 0

    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None


    def buy_signal(self, signal, price):
        if self.accnt.sell_only():
            return False

        if self.accnt.btc_only() and self.currency != 'BTC':
            return False

        if float(signal.buy_price) != 0.0 or self.disable_buy:
            return False

        # check USDT value of base by calculating (base_currency) * (currency_usdt)
        # verify that USDT value >= $0.02, if less do not buy
        usdt_symbol = self.accnt.make_ticker_id(self.currency, 'USDT')
        currency_price = float(self.accnt.get_ticker(usdt_symbol))
        if currency_price:
            price_usdt = currency_price * price
            if price_usdt < 0.02:
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

        if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
            return False

        # if it's been over 8 hours since buy executed for symbol, sell as soon as percent profit > 0
        if (self.timestamp - signal.last_buy_ts) > self.accnt.hours_to_ts(8):
            return True

        # if buying is disabled and symbol is >= 1.0 percent profit, then sell
        if self.disable_buy:
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
        self.logger.info("loading into {} price={} size={} sigid={}".format(self.ticker_id, buy_price, buy_size, sig_id))

    # NOTE: low and high do not update for each kline with binance
    ## mmkline is kline from MarketManager which is filtered and resampled
    def run_update(self, kline, mmkline=None, cache_db=None):
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
            volume = kline.volume_quote
            self.timestamp = kline.ts

        if close == 0 or volume == 0:
            return

        if self.timestamp == self.last_timestamp:
            return

        self.signal_handler.pre_update(close=close, volume=kline.volume_quote, ts=self.timestamp, cache_db=cache_db)

        completed = False

        if not self.msg_handler.empty():
            for msg in self.msg_handler.get_messages(src_id=Message.ID_MULTI, dst_id=self.ticker_id):
                if not msg:
                    continue
                if msg.cmd == Message.MSG_BUY_COMPLETE:
                    #self.logger.info("BUY_COMPLETE for {} price={} size={}".format(msg.dst_id,
                    #                                                             msg.price,
                    #                                                             msg.size))
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    signal.buy_price = msg.price
                    msg.mark_read()
                    completed = True
                    #if msg.order_type == Message.TYPE_MARKET:
                    #    # Also place trailing stop loss
                    #    self.set_sell_stop_loss(signal, close)
                elif msg.cmd == Message.MSG_SELL_COMPLETE:
                    #self.logger.info("SELL_COMPLETE for {} price={} buy_price={} size={}".format(msg.dst_id,
                    #                                                                           msg.price,
                    #                                                                           msg.buy_price,
                    #                                                                           msg.size))
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    signal.last_sell_price = msg.price
                    if msg.order_type == Message.TYPE_MARKET:
                        self.cancel_sell_stop_loss(signal)
                    self.stop_loss_set = False
                    self.stop_loss_price = 0
                    self.next_stop_loss_price = 0
                    msg.mark_read()
                    completed = True
                elif msg.cmd == Message.MSG_BUY_FAILED:
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    self.logger.info("BUY_FAILED for {} price={} size={}".format(msg.dst_id,
                                                                                 msg.price,
                                                                                 msg.size))
                    if self.min_trade_size_qty != 1.0:
                        self.min_trade_size_qty = 1.0
                    signal.buy_price = 0.0
                    signal.buy_size = 0.0
                    signal.buy_timestamp = 0
                    # for failed buy, disable buys for this symbol for 4 hours
                    signal.disabled = True
                    signal.disabled_end_ts = signal.timestamp + self.accnt.hours_to_ts(4)
                    msg.mark_read()
                elif msg.cmd == Message.MSG_SELL_FAILED:
                    id = msg.sig_id
                    signal = self.signal_handler.get_handler(id=id)
                    self.logger.info("SELL_FAILED for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                               msg.price,
                                                                                               msg.buy_price,
                                                                                               msg.size))
                    signal.buy_price = signal.last_buy_price
                    if self.stop_loss_set:
                        self.cancel_sell_stop_loss(signal)
                        self.stop_loss_set = False
                        self.stop_loss_price = 0
                        self.next_stop_loss_price = 0

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
            signal.buy_timestamp = self.timestamp
            signal.last_buy_ts = self.timestamp

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
            signal.last_sell_ts = self.timestamp

        # prevent buying at the same price with the same timestamp with more than one signal
        if self.signal_handler.is_duplicate_buy(price, self.timestamp):
            return

        if signal.get_flag() == SignalBase.FLAG_SELL_ALL:
            balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
            if balance_available != 0 and signal.sell_signal():
                self.msg_handler.sell_market(self.ticker_id, price, balance_available, price, sig_id=signal.id)

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

        if not self.stop_loss_set:
            if not self.stop_loss_price:
                self.stop_loss_price = signal.buy_price
            if StrategyBase.percent_p2_gt_p1(self.stop_loss_price, price, 1.0):
                self.set_sell_stop_loss(signal, self.stop_loss_price)
                self.next_stop_loss_price = price
        elif StrategyBase.percent_p2_gt_p1(self.next_stop_loss_price, price, 1.0):
                self.cancel_sell_stop_loss(signal)
                self.stop_loss_price = self.next_stop_loss_price
                self.set_sell_stop_loss(signal, self.stop_loss_price)
                self.next_stop_loss_price = price


    def set_sell_stop_loss(self, signal, price):
        if self.stop_loss_set:
            return False
        #self.logger.info("set_sell_stop_loss({}, {}, {})".format(self.ticker_id, price, signal.buy_size))
        self.msg_handler.sell_stop_loss(self.ticker_id, price, signal.buy_size, signal.buy_price, signal.id)
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
        signal.buy_timestamp = self.timestamp
        signal.last_buy_ts = self.timestamp
        signal.sell_timestamp = 0

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
            # for trader running live. Delay setting buy_price until next price
            self.update_buy_price = True


    def sell_market(self, signal, price):
        if float(signal.buy_price) == 0:
            return

        sell_price = price

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

            if self.min_trade_size_qty != 1.0:
                self.min_trade_size_qty = 1.0

            signal.last_buy_price = signal.buy_price
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.last_sell_price = sell_price
            signal.last_sell_ts = self.timestamp
            signal.buy_timestamp = 0
            signal.sell_timestamp = self.timestamp

            # for trader running live. Delay setting sell_price until next price
            self.update_sell_price = True
