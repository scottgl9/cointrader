from trader import OrderBookGDAX
from trader import AccountGDAX
from trader import OrderHandler
from trader.indicator import SMMA, EMA
from trader.account import gdax


class buy_low_sell_high:
    def __init__(self, client, name='BTC', currency='USD', account_handler=None, order_handler=None):
        self.client = client
        if not account_handler:
            self.accnt = AccountGDAX(self.client, name, currency)
        else:
            self.accnt = account_handler
        self.products = [self.accnt.ticker_id]
        self.orderbook = OrderBookGDAX()
        if not order_handler:
            self.order_handler = OrderHandler(self.accnt)
        self.smma = SMMA.SMMA(14)
        self.ema = EMA.EMA(30)
        self.ema_last_price = self.smma_last_price = 0.0
        self.last_signal_price = 0.0
        self.watch_sell = False
        self.watch_buy = False
        self.pc = gdax.PublicClient()

        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.last_high_24hr = 0.0
        self.last_low_24hr = 0.0
        self.last_50_prices = []
        #self.update_24hr_stats()
        print("Started {} strategy".format(self.__class__.__name__))

    def get_ticker_id(self):
        return self.accnt.ticker_id

    def price_near_24hr(self, price, percent=5.0, percent_cutoff_buy=6.0, percent_cutoff_sell=7.0):
        if self.high_24hr == 0.0 or self.low_24hr == 0.0:
            return
        buy_signal = False
        sell_signal = False
        high_threshold = (1.0 - percent/100.0) * self.high_24hr
        low_threshold = (1.0 + percent/100.0) * self.low_24hr
        high_cutoff = (1.0 - percent_cutoff_sell/100.0) * self.high_24hr
        low_cutoff = (1.0 + percent_cutoff_buy/100.0) * self.low_24hr

        if price >= high_threshold:
            self.watch_sell = True
            #sell_signal = True

        if price <= low_threshold:
            self.watch_buy = True
            #buy_signal = True

        if price >= high_cutoff and price < high_threshold and self.watch_sell:
            sell_signal = True

        if price <= low_cutoff and price > low_threshold and self.watch_buy:
            buy_signal = True

        if buy_signal and sell_signal:
            buy_signal = False
            sell_signal = False

        #if buy_signal and self.last_signal_price != 0.0 and (self.last_signal_price - price) / self.last_signal_price < 0.01:
        #    buy_signal = False
        #elif sell_signal and self.last_signal_price != 0.0 and (price - self.last_signal_price) / self.last_signal_price < 0.01:
        #    sell_signal = False

        return {'buy': buy_signal, 'sell': sell_signal}

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def update_last_50_prices(self, price):
        self.last_50_prices.append(price)
        if len(self.last_50_prices) > 50:
            diff_size = len(self.last_50_prices) - 50
            self.last_50_prices = self.last_50_prices[diff_size:]

    def run_update_price(self, msg):
        if 'type' in msg and 'match' not in msg['type']: return

        price = float(msg["price"])
        self.update_last_50_prices(price)
        self.accnt.market_price = price
        smma_price = float(self.smma.update(price))
        ema_price = float(self.ema.update(price))

        signal = self.price_near_24hr(price)

        if signal['buy'] and ema_price < self.ema_last_price:
            self.last_signal_price = price
            #print("buy signal: high={}, low={}, price={}".format(self.high_24hr, self.low_24hr, price))
            size = self.accnt.quote_currency_balance / price
            if size >= 0.01:
                if self.last_high_24hr != 0.0 and self.last_low_24hr != 0.0 and self.high_24hr > self.last_low_24hr\
                        and self.high_24hr > self.last_high_24hr:
                    self.accnt.buy_market(size)
                self.watch_buy = False
                self.last_low_24hr = self.low_24hr
                self.last_high_24hr = self.high_24hr
        elif signal['sell'] and ema_price > self.ema_last_price:
            self.last_signal_price = price
            #print("sell signal: high={}, low={}, price={}".format(self.high_24hr, self.low_24hr, price))
            if self.accnt.funds_available >= 0.01:
                if self.last_high_24hr != 0.0 and self.last_low_24hr != 0.0 and self.low_24hr < self.last_high_24hr\
                        and self.low_24hr < self.last_low_24hr:
                    self.accnt.sell_market(self.accnt.funds_available)
                self.watch_sell = False
                self.last_low_24hr = self.low_24hr
                self.last_high_24hr = self.high_24hr

        self.smma_last_price = smma_price
        self.ema_last_price = ema_price

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)

    def close(self):
        pass