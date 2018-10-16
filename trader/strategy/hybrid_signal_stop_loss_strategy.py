from trader.lib.MessageHandler import Message, MessageHandler
from trader.signal import select_signal_name
from trader.strategy.StrategyBase import StrategyBase
from trader.strategy.trade_size_strategy.static_trade_size import static_trade_size
from trader.signal.SignalBase import SignalBase
from trader.signal.SignalHandler import SignalHandler
from trader.indicator.OBV import OBV
from trader.lib.SupportResistLevels import SupportResistLevels
from trader.lib.StatTracker import StatTracker
from datetime import datetime


class hybrid_signal_stop_loss_strategy(StrategyBase):
    def __init__(self, client, base='BTC', currency='USD', signal_names=None, account_handler=None, base_min_size=0.0, tick_size=0.0, logger=None):
        super(hybrid_signal_stop_loss_strategy, self).__init__(client,
                                                               base,
                                                               currency,
                                                               account_handler,
                                                               base_min_size,
                                                               tick_size,
                                                               logger)
        self.strategy_name = 'hybrid_signal_stop_loss_strategy'
        self.last_price = self.price = 0.0
        self.last_close = 0.0

        if signal_names:
            for name in signal_names:
                self.signal_handler.add(select_signal_name(name))
        else:
            self.signal_handler.add(select_signal_name("Hybrid_Crossover"))

        self.obv = OBV()
        self.low_short = self.high_short = 0.0
        self.low_long = self.high_long = 0.0
        self.prev_low_long = self.prev_high_long = 0.0
        self.prev_low_short = self.prev_high_short = 0.0

        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.timestamp = 0
        self.last_timestamp = 0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.interval_price = 0.0
        self.trend_upward_count = 0
        self.trend_downward_count = 0
        self.last_price = 0.0
        self.min_trade_size = 0.0 #self.base_min_size * 20.0
        self.min_trade_size_qty = 1.0
        self.min_price = 0.0
        self.max_price = 0.0
        self.trade_size_handler = static_trade_size(base, currency, base_min_size, tick_size, usdt=10)

    # clear pending sell trades which have been bought
    def reset(self):
        for signal in self.signal_handler.get_handlers():
            signal.buy_price = 0.0
            signal.buy_size = 0.0
            signal.buy_order_id = None
            signal.buy_pending = False
            signal.sell_pending = False
            signal.buy_pending_price = 0.0
            signal.sell_pending_price = 0.0
            signal.last_sell_price = 0.0


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
        # check balance to see if we have enough to sell
        balance_available = self.round_base(float(self.accnt.get_asset_balance_tuple(self.base)[1]))
        if balance_available < float(self.min_trade_size):
            return False

        if float(signal.buy_price) == 0.0:
            return False

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

        self.obv.update(close, volume)

        self.signal_handler.pre_update(close=close, volume=volume, ts=self.timestamp)

        for signal in self.signal_handler.get_handlers():
            self.run_update_signal(signal, close)

        self.last_timestamp = self.timestamp
        self.last_price = close
        self.last_close = close


    def run_update_signal(self, signal, price):
        buy_price = price + self.quote_increment * 2
        sell_price = price - self.quote_increment * 2
        if not signal.buy_pending and self.buy_signal(signal, price):
            if 'e' in str(self.min_trade_size):
                return

            min_trade_size = self.min_trade_size

            if self.min_trade_size_qty != 1.0:
                min_trade_size = float(min_trade_size) * self.min_trade_size_qty

            #buy_price = price + self.quote_increment
            buy_size = min_trade_size

            self.msg_handler.buy_stop_loss(self.ticker_id, buy_price, buy_size, signal.id)
            signal.buy_pending = True
            signal.buy_pending_price = buy_price

        if not signal.sell_pending and self.sell_signal(signal, price):
            sell_price = price - self.quote_increment
            self.msg_handler.sell_stop_loss(self.ticker_id, sell_price, signal.buy_size, signal.buy_price, signal.id)
            signal.sell_pending = True
            signal.sell_pending_price = sell_price

        if signal.buy_pending:
            msg = self.msg_handler.get_first_message(src_id=Message.ID_MULTI, dst_id=self.ticker_id, sig_id=signal.id)
            if not msg:
                if self.buy_signal(signal, price):
                    # if we received a new buy signal with order pending, cancel order and replace
                    #buy_price = price + self.quote_increment
                    buy_size = self.min_trade_size

                    if self.min_trade_size_qty != 1.0:
                        buy_size = float(buy_size) * self.min_trade_size_qty

                    self.msg_handler.buy_replace(self.ticker_id, buy_price, buy_size, signal.id)
                    return
                elif signal.buy_pending_price != 0 and abs(price - signal.buy_pending_price) / signal.buy_pending_price > 0.02:
                    # price has fallen another 5%, cancel old order and create new lower one
                    #buy_price = price + self.quote_increment
                    signal.buy_pending_price = buy_price
                    buy_size = self.min_trade_size

                    if self.min_trade_size_qty != 1.0:
                        buy_size = float(buy_size) * self.min_trade_size_qty

                    self.msg_handler.buy_replace(self.ticker_id, buy_price, buy_size, signal.id)
                return

            if msg.cmd == Message.MSG_BUY_COMPLETE:
                signal.buy_price = float(msg.price)
                signal.buy_size = float(msg.size)
                signal.buy_timestamp = self.timestamp
                signal.buy_pending = False
                msg.mark_read()
                self.msg_handler.clear_read()
            elif msg.cmd == Message.MSG_BUY_FAILED:
                id = msg.sig_id
                self.logger.info("BUY_FAILED for {} price={} size={}".format(msg.dst_id,
                                                                             msg.price,
                                                                             msg.size))
                if self.min_trade_size_qty != 1.0:
                    self.min_trade_size_qty = 1.0
                signal.buy_price = 0.0
                signal.buy_size = 0.0
                signal.buy_timestamp = 0
                signal.buy_pending = False
                signal.buy_pending_price = 0
                msg.mark_read()
                self.msg_handler.clear_read()
        elif signal.sell_pending:
            msg = self.msg_handler.get_first_message(src_id=Message.ID_MULTI, dst_id=self.ticker_id, sig_id=signal.id)
            if not msg:
                if self.sell_signal(signal, price):
                    # if we received a new sell signal with order pending, cancel order and replace
                    #sell_price = price - self.quote_increment
                    self.msg_handler.sell_replace(self.ticker_id, sell_price, signal.buy_size, signal.buy_price, signal.id)
                    return
                elif signal.sell_pending_price != 0 and abs(price - signal.sell_pending_price) / signal.sell_pending_price > 0.01:
                    # price has risen another 5%, cancel old order and create new higher one
                    #sell_price = price - self.quote_increment
                    signal.sell_pending_price = sell_price

                    self.msg_handler.sell_replace(self.ticker_id, sell_price, signal.buy_size, signal.buy_price, signal.id)
                return

            if msg.cmd == Message.MSG_SELL_COMPLETE:
                signal.last_buy_price = signal.buy_price
                signal.buy_price = 0.0
                signal.buy_size = 0.0
                signal.last_sell_price = msg.price
                signal.buy_timestamp = 0
                signal.sell_pending = False

                if self.min_trade_size_qty != 1.0:
                    self.min_trade_size_qty = 1.0

                msg.mark_read()
                self.msg_handler.clear_read()
            elif msg.cmd == Message.MSG_SELL_FAILED:
                self.logger.info("SELL_FAILED for {} price={} buy_price={} size={}".format(msg.dst_id,
                                                                                           msg.price,
                                                                                           msg.buy_price,
                                                                                           msg.size))
                msg.mark_read()
                self.msg_handler.clear_read()
