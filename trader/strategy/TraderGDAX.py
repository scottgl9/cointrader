#from pymongo import MongoClient
from trader import OrderBookGDAX
from trader.indicator import SMMA, EMA
from trader import AccountGDAX
from trader import OrderHandler
import time

class TraderGDAX:
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
        self.accnt.cancel_all()
        time.sleep(1)
        print(self.accnt.get_account_balance())

        self.smma = SMMA(14)
        self.ema = EMA(30)
        self.last_time = ''
        self.last_price = 0.0
        self.current_bids_price = 0.0
        self.current_asks_price = 0.0
        self.ema_last_price = self.smma_last_price = 0.0
        self.smma_trending_downward_count = self.smma_trending_upward_count = 0
        self.price_trending_downward_count = self.price_trending_upward_count = 0

        self.price_start = self.price_end = 0.0
        self.last_price_start = self.last_price_end = 0.0
        self.last_buy_price = self.last_sell_price = 0.0
        self.last_price_checked = 0.0
        self.buy_price = 0.0
        self.buy_order_id = ''
        self.buy_pending_count = 0
        self.buy_pending = False
        self.buy_price = 0.0
        self.buy_amount = 0.0
        self.sell_price = 0.0
        self.sell_amount = 0.0
        self.sell_pending = False
        self.sell_pending_count = 0
        self.buy_failed = False

        self.direction = 0
        self.total_count = 0

        self.order_handler.get_buy_price_list()

    def get_ticker_id(self):
        return self.accnt.ticker_id

    # update account balance from GDAX
    def update_account_balance(self):
        self.accnt.get_account_balance()
        self.balance_usd = self.accnt.quote_currency_balance
        self.balance_btc = self.accnt.balance
        self.balance_usd_available = self.accnt.quote_currency_available
        self.balance_btc_available = self.accnt.funds_available

    def detect_trend_change_upward(self, smma_price, ema_price, price, direction):
        if self.smma_last_price == 0.0 or self.ema_last_price == 0.0:
            return False

        # SMMA hasn't changed or is below last price
        if smma_price < self.smma_last_price:
            return False

        if self.ema_last_price > ema_price: # or smma_price < ema_price: # or smma_price > price:
            return False

        if self.smma_trending_downward_count > 0: self.smma_trending_downward_count = 0
        self.smma_trending_upward_count += 1

        if direction != 0 and direction < 1:
            return False

        #if self.smma_trending_upward_count < 2: return False

        return True

    def detect_trend_change_downward(self, smma_price, ema_price, price, direction):
        if self.smma_last_price == 0.0 or self.ema_last_price == 0.0:
            return False

        if smma_price > self.smma_last_price:
            return False

        if self.ema_last_price < ema_price: # or smma_price > ema_price: #or smma_price < price:
            return False

        if self.smma_trending_upward_count > 0: self.smma_trending_upward_count = 0
        self.smma_trending_downward_count += 1

        if direction != 0 and direction > -1:
            return False

        #if self.smma_trending_downward_count < 2: return False

        return True

    def detect_market_direction_orders(self, price):
        self.top_bids = self.orderbook.get_bids_distribution_by_range(price - 10.0, price + 10.0, cutoff=0.0)
        self.top_asks = self.orderbook.get_asks_distribution_by_range(price - 10.0, price + 10.0, cutoff=0.0)

        if self.top_bids and self.top_asks:
            top_bid = self.top_bids[-1]
            top_ask = self.top_asks[0]
            if top_ask[0] == (top_bid[0] + self.accnt.quote_increment):
                if top_ask[1] < 5.0 and top_bid[1] >= 80.0:
                    self.direction = 3
                if (top_ask[1] < 10.0 and top_bid[1] >= 30.0):
                    self.direction = 2
                elif (top_bid[1] >= 10.0 and top_bid[1] >= (top_ask[1] * 4.0)):
                    self.direction = 2
                elif (top_bid[1] >= 10.0 and top_bid[1] >= (top_ask[1] * 3.0)):
                    self.direction = 1
                if top_bid[1] < 5.0 and top_ask[1] >= 80.0:
                    self.direction = -3
                elif (top_bid[1] < 10.0 and top_ask[1] >= 30.0):
                    self.direction = -2
                elif (top_ask[1] >= 10.0 and (top_bid[1] * 4.0) <= top_ask[1]):
                    self.direction = -2
                elif (top_ask[1] >= 10.0 and (top_bid[1] * 3.0) <= top_ask[1]):
                    self.direction = -1
                else:
                    self.direction = 0
            else:
                if price in self.top_bids and self.top_bids[price] >= 40:
                    self.direction = 2
                elif price in self.top_asks and self.top_asks[price] >= 40:
                    self.direction = -2
                else:
                    self.direction = 0

    def price_movement_indicator(self, market_price):
        if 1: #market_price != self.last_price_checked:
            #self.last_price_start = self.price_start
            #self.last_price_end = self.price_end
            self.price_start, self.price_end, self.weight, self.resistance,\
                self.oprice, self.oweight = self.orderbook.compute_expected_price_movement(market_price)

            # case when price is moving up
            #if self.price_start != 0.0 and self.price_start < self.price_end and (self.price_end + 5.0) > self.price_start and self.weight > 5.0 and self.weight > (2.0 * self.resistance):
            if self.weight > 5.0 and self.weight > (2.0 * self.resistance) and self.order_handler.in_sell_range(self.price_start, self.price_end, 5.0) == False:
                #if self.order_handler.in_price_range(self.price_start, self.price_end):
                #if self.direction == -1:
                #    self.accnt.cancel_all()

                if self.current_asks_price != 0.0 and self.current_asks_price > self.price_start:
                    self.price_start = self.current_asks_price + 2.0
                elif market_price > self.price_start:
                    self.price_start = market_price + 2.0

                #if abs(self.price_start - self.last_price_start) > 5.0 and abs(self.price_end - self.last_price_end) > 5.0:
                if 1:
                    print("expecting UPWARD price move from %f to %f (weight=%f, resistance=%f, oprice=%f, oweight=%f, price=%f)" % (
                            self.price_start, self.price_end, self.weight, self.resistance, self.oprice, self.oweight,
                            self.last_price))
                    self.order_handler.orders_pending_handler_sandbox(market_price)
                    self.price_start += 1.0
                    self.price_end += 1.0
                    increment = 2.0 #(self.price_end-self.price_start)/2.0
                    price = self.price_start
                    price_list = []
                    while price <= self.price_end:
                        if price in self.order_handler.buy_price_list: continue
                        if self.order_handler.sell_limit_spread(price, spread=0.0, sell_size=0.01) != 0.0:
                            price_list.append(price)
                        price += increment
                    if len(price_list) != 0: print("send sell orders = {}".format(price_list))
                    self.price_start -= 1.0
                    self.price_end -= 1.0
                    self.last_sell_price = self.price_start
                self.direction = 1
            # case when price is moving down
            #elif self.price_end != 0.0 and self.price_start > self.price_end and (self.price_end - 5.0) < self.price_start and self.weight > 5.0 and self.weight > (2.0 * self.resistance)# :
            elif self.weight > 5.0 and self.weight > (2.0 * self.resistance) and self.order_handler.in_buy_range(self.price_start, self.price_end, 5.0) == False:
                #if self.direction == 1:
                #    self.accnt.cancel_all()

                if self.current_bids_price != 0.0 and self.current_bids_price < self.price_start:
                    self.price_start = self.current_bids_price - 2.0
                elif market_price < self.price_start:
                    self.price_start = market_price - 2.0

                #if abs(self.price_start - self.last_price_start) > 5.0 and abs(self.price_end - self.last_price_end) > 5.0:
                if 1:
                    self.order_handler.orders_pending_handler_sandbox(market_price)
                    print("expecting DOWNWARD price move from %f to %f (weight=%f, resistance=%f, oprice=%f, oweight=%f, price=%f)" % (
                    self.price_start, self.price_end, self.weight, self.resistance, self.oprice, self.oweight, self.last_price))
                    #self.accnt.cancel_all()
                    self.price_start -= 1.0
                    self.price_end -= 1.0
                    increment = -2.0 #(self.price_end-self.price_start)/2.0
                    price = self.price_start
                    price_list = []
                    while price >= self.price_end:
                            if self.order_handler.buy_limit_spread(price, spread=0.0, buy_size=0.01) != 0.0:
                                price_list.append(price)
                            price += increment
                    print("send buy orders = {}".format(price_list))
                    self.price_start += 1.0
                    self.price_start += 1.0
                    self.last_buy_price = self.price_start
                    self.direction = -1
        self.last_price_checked = market_price

    def run_update_price(self, msg):
        self.top_asks = None
        self.top_bids = None

        #self.orders_pending_handler_sandbox(msg)

        if 'type' in msg and 'match' not in msg['type']: return
        price = float(msg["price"])

        smma_price = float(self.smma.update(price))
        ema_price = float(self.ema.update(price))

        # self.detect_market_direction_orders(price)

        if self.last_price != 0.0:
            if price > self.last_price:
                if self.price_trending_downward_count > 0: self.price_trending_downward_count = 0
                self.price_trending_upward_count += 1

            elif price < self.last_price:
                if self.price_trending_upward_count > 0: self.price_trending_upward_count = 0
                self.price_trending_downward_count += 1

        # has there been an upward move on the SMMA?
        if self.detect_trend_change_upward(smma_price, ema_price, price, self.direction):
            if self.direction >= 2:
                self.order_handler.orders_pending_handler_sandbox(price)
                self.order_handler.sell_limit_spread(price, sell_size=0.005)

        # has there been a downward move on the SMMA?
        if self.detect_trend_change_downward(smma_price, ema_price, price, self.direction):
            if self.direction <= -2:
                self.order_handler.orders_pending_handler_sandbox(price)
                self.order_handler.buy_limit_spread(price, buy_size=0.005)

        self.smma_last_price = smma_price
        self.ema_last_price = ema_price
        if msg['side'] == 'buy':
            self.current_bids_price = price
        elif msg['side'] == 'sell':
            self.current_asks_price = price
        self.total_count += 1
        self.price_movement_indicator(price)

    def run_update_orderbook(self, msg):
        self.orderbook.process_update(msg)
        self.price_movement_indicator(self.last_price)

    def get_products(self):
        return self.accnt.ticker_id

    def close(self):
        self.accnt.cancel_all()
        self.update_account_balance()
        #self.save_buy_price_list()
        print("-- Goodbye! --")
        print("Initial balance USD=%f BTC=%f" % (self.order_handler.initial_balance_usd, self.order_handler.initial_balance_btc))
        print("Final balance USD=%f BTC=%f @ (%f)" % (self.order_handler.balance_usd, self.order_handler.balance_btc, self.last_price))
