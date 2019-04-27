from trader.lib.Message import Message
from trader.lib.MessageHandler import MessageHandler
from trader.strategy.trade_size_strategy.static_trade_size import static_trade_size
from trader.strategy.trade_size_strategy.fixed_trade_size import fixed_trade_size
from trader.strategy.trade_size_strategy.percent_balance_trade_size import percent_balance_trade_size
from trader.strategy.StrategyBase import StrategyBase, select_hourly_signal
from trader.signal.SignalBase import SignalBase
import time
from datetime import datetime


class basic_signal_market_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', signal_names=None, hourly_signal_name=None,
                 account_handler=None, order_handler=None, hourly_klines_handler=None, asset_info=None,
                 base_min_size=0.0, tick_size=0.0, logger=None):
        super(basic_signal_market_strategy, self).__init__(client,
                                                           base,
                                                           currency,
                                                           account_handler,
                                                           order_handler,
                                                           hourly_klines_handler,
                                                           base_min_size,
                                                           tick_size,
                                                           asset_info,
                                                           logger)
        self.strategy_name = 'hybrid_signal_market_strategy'
        self.trade_size_handler = fixed_trade_size(self.accnt,
                                                   asset_info,
                                                   btc=0.004,
                                                   eth=0.1,
                                                   bnb=3,
                                                   pax=10.0,
                                                   usdt=10.0,
                                                   multiplier=5.0)


        if hourly_signal_name:
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

        if not StrategyBase.percent_p2_gt_p1(signal.buy_price, price, 1.0):
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
                    signal.buy_size = msg.size
                    signal.buy_price = msg.price
                    signal.buy_timestamp = self.timestamp
                    signal.last_buy_ts = self.timestamp
                    msg.mark_read()
                    completed = True
                elif msg.cmd == Message.MSG_SELL_COMPLETE:
                    if not self.simulate:
                        self.logger.info("SELL_COMPLETE for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                                     msg.price,
                                                                                                     msg.buy_price,
                                                                                                     msg.size))
                    signal = self.signal_handler.get_handler(id=msg.sig_id)
                    signal.last_sell_price = msg.price
                    if self.min_trade_size_qty != 1.0:
                        self.min_trade_size_qty = 1.0

                    signal.last_buy_price = msg.buy_price
                    signal.buy_price = 0.0
                    signal.buy_size = 0.0
                    signal.last_sell_price = msg.price
                    signal.buy_timestamp = 0
                    signal.last_sell_ts = self.timestamp

                    # if buy price was loaded from trade.db, mark buy_loaded as fail since it was sold
                    self.buy_loaded = False

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
        if self.simulate:
            # end_ts is first ts for simulation, so adjust ts to 2 hours ago (just to be safe):
            end_ts = ts - self.accnt.hours_to_ts(2)
            start_ts = end_ts - self.accnt.hours_to_ts(48)
            self.hourly_klines_signal.load(start_ts, end_ts, ts)
            self.accnt.loaded_model_count += 1

    def run_update(self, kline, mmkline=None, cache_db=None):
        close = kline.close
        self.low = kline.low
        self.high = kline.high
        volume = kline.volume_quote

        if not self.timestamp:
            if self.simulate and self.hourly_klines_signal and not self.hourly_klines_loaded:
                #if self.accnt.loaded_model_count <= 5:
                if self.ticker_id.endswith('USDT'):
                    self.load_hourly_klines(kline.ts)
                    self.hourly_klines_loaded = True
                else:
                    self.hourly_klines_disabled = True

        self.timestamp = kline.ts

        if close == 0 or volume == 0:
            return

        if self.timestamp == self.last_timestamp:
            return

        if self.hourly_klines_signal and not self.hourly_klines_disabled:
            self.hourly_klines_signal.update(ts=self.timestamp)

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

        if signal.get_flag() == SignalBase.FLAG_SELL_ALL:
            balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
            if balance_available != 0 and signal.sell_signal():
                self.msg_handler.sell_market(self.ticker_id, price, balance_available, price, sig_id=signal.id)

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

        min_trade_size = self.min_trade_size

        if self.min_trade_size_qty != 1.0:
            min_trade_size = float(min_trade_size) * self.min_trade_size_qty

        signal.buy_price = price
        signal.buy_size = min_trade_size

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

