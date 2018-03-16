# Place, track, and manage orders
import sys
from inspect import currentframe, getsourcefile
import trader.account.gdax as gdax
from collections import OrderedDict
import uuid

#[[{u'status': u'open', u'created_at': u'2018-03-10T07:30:11.066886Z', u'post_only': True, u'product_id': u'BTC-USD', u'fill_fees': u'0.0000000000000000', u'settled': False, u'price': u'9464.17000000', u'executed_value': u'0.0000000000000000', u'id': u'924af4b5-c522-4696-a4a3-79dc82fb671d', u'time_in_force': u'GTC', u'filled_size': u'0.00000000', u'type': u'limit', u'side': u'sell', u'size': u'0.00100000'},
#{u'status': u'open', u'created_at': u'2018-03-10T07:28:27.613741Z', u'post_only': True, u'product_id': u'BTC-USD', u'fill_fees': u'0.0000000000000000', u'settled': False, u'price': u'9465.03000000', u'executed_value': u'0.0000000000000000', u'id': u'6def5aa6-8635-4a7b-bc29-600b125db462', u'time_in_force': u'GTC', u'filled_size': u'0.00000000', u'type': u'limit', u'side': u'sell', u'size': u'0.00100000'}]]


class OrderHandler:
    def __init__(self, accnt):
        self.DEBUG()
        self.accnt = accnt
        self.market_price = 0.0
        self.market_fee = 0.0015 #0.0025
        self.pending_limit_buy_orders = []
        self.pending_limit_sell_orders = []
        self.buy_fail_count = 0
        self.sell_fail_count = 0
        self.buy_price = 0.0
        self.buy_price_list = []
        self.pending_buy_price_list = []
        self.pending_sell_price_list = []
        self.min_pending_buy_price = 0.0
        self.max_pending_buy_price = 0.0
        self.min_pending_sell_price = 0.0
        self.max_pending_sell_price = 0.0
        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

        self.orders_canceled = 0
        self.pc = gdax.PublicClient()
        self.ticker_id = self.accnt.ticker_id

        #self.accnt.cancel_all()
        self.accnt.get_account_balance()

        # OrderHandler run stats
        self.limit_buy_orders_placed = 0
        self.limit_buy_orders_canceled = 0
        self.limit_sell_orders_placed = 0
        self.limit_sell_orders_canceled = 0
        self.limit_buy_orders_failed_reason1 = 0
        self.limit_buy_orders_failed_reason2 = 0
        self.limit_buy_orders_failed_reason3 = 0
        self.limit_buy_orders_failed_reason4 = 0
        self.limit_sell_orders_failed_reason1 = 0
        self.limit_sell_orders_failed_reason2 = 0
        self.limit_sell_orders_failed_reason3 = 0
        self.limit_sell_orders_failed_reason4 = 0
        self.limit_buy_orders_pending_count = 0
        self.limit_sell_orders_pending_count = 0
        self.limit_sell_order_price_too_low = 0
        self.market_buy_orders_failed_reason1 = 0
        self.market_sell_orders_failed_reason1 = 0

        pc = gdax.PublicClient()
        for product in pc.get_products():
            if 'id' in product and product['id'] == self.ticker_id:
                self.quote_increment = float(product['quote_increment'])
                self.base_min_size = float(product['base_min_size'])
                self.min_market_funds = float(product['min_market_funds'])
                break

        self.pending_limit_buy_orders = self.accnt.get_open_buy_orders()
        for order in self.pending_limit_buy_orders:
            self.pending_buy_price_list.append(order[0])

        print("pending_buy_price_list")
        print(self.pending_buy_price_list)

        self.pending_limit_sell_orders = self.accnt.get_open_sell_orders()
        for order in self.pending_limit_sell_orders:
            self.pending_sell_price_list.append(order[0])
        print("pending_sell_price_list:")
        print(self.pending_sell_price_list)

        #if not self.accnt.simulation:
        self.buy_price_list, self.sell_price_list = self.accnt.preload_buy_price_list()
        if len(self.sell_price_list) > 0:
            self.last_sell_price = self.sell_price_list[0]
        print(self.buy_price_list)
        print(self.sell_price_list)

        print("Order Handler Started")
        #self.low_4hr, self.high_4hr = self.accnt.get_4hr_stats()
        #print(self.low_4hr, self.high_4hr)
        #self.count_4hr = 0
        self.update_24hr_stats()
        print(self.orders_completed_balance(float(self.accnt.close_24hr)))

    def DEBUG(self):
        cf = currentframe()
        #args = inspect.getargspec(cf.f_back.f_code)[0].
        print("file {} line {} function {}".format(getsourcefile(self.__class__), cf.f_back.f_lineno, cf.f_back.f_code.co_name))

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.accnt.ticker_id)
        print(stats)
        self.accnt.high_24hr = float(stats['high'])
        self.accnt.low_24hr = float(stats['low'])
        self.accnt.open_24hr = float(stats['open'])
        self.accnt.close_24hr = float(stats['last'])
        self.accnt.volume_24hr = float(stats['volume'])

    def print_stats(self):
        self.update_24hr_stats()
        self.accnt.get_account_balance()
        print("balance ({}): {}".format(self.accnt.currency, self.accnt.quote_currency_balance))
        print("available funds ({}): {}".format(self.accnt.currency, self.accnt.quote_currency_available))
        print("balance ({}): {}".format(self.accnt.base_currency, self.accnt.balance))
        print("available funds ({}): {}".format(self.accnt.base_currency, self.accnt.funds_available))
        print("quote increment: {} min size: {}".format(self.accnt.quote_increment, self.accnt.base_min_size))
        print("high: {} low: {} open: {}".format(self.accnt.high_24hr, self.accnt.low_24hr, self.accnt.open_24hr))
        print("pending limit buy orders: {}".format(self.pending_limit_buy_orders))
        print("pending limit sell orders: {}".format(self.pending_limit_sell_orders))

    def run_stats_dict(self):
        stats = OrderedDict()
        stats['limit_buy_orders_placed'] = self.limit_buy_orders_placed
        stats['limit_buy_orders_canceled'] = self.limit_buy_orders_canceled
        stats['limit_sell_orders_placed'] = self.limit_sell_orders_placed
        stats['limit_sell_orders_canceled'] = self.limit_sell_orders_canceled
        stats['limit_buy_orders_failed_reason1'] = self.limit_buy_orders_failed_reason1
        stats['limit_buy_orders_failed_reason2'] = self.limit_buy_orders_failed_reason2
        stats['limit_buy_orders_failed_reason3'] = self.limit_buy_orders_failed_reason3
        stats['limit_buy_orders_failed_reason4'] = self.limit_buy_orders_failed_reason4
        stats['limit_sell_orders_failed_reason1'] = self.limit_sell_orders_failed_reason1
        stats['limit_sell_orders_failed_reason2'] = self.limit_sell_orders_failed_reason2
        stats['limit_sell_orders_failed_reason3'] = self.limit_sell_orders_failed_reason3
        stats['limit_sell_orders_failed_reason4'] = self.limit_sell_orders_failed_reason4
        stats['limit_buy_orders_pending_count'] = self.limit_buy_orders_pending_count
        stats['limit_sell_orders_pending_count'] = self.limit_sell_orders_pending_count
        stats['limit_sell_order_price_too_low'] = self.limit_sell_order_price_too_low
        stats['market_buy_orders_failed_reason1'] = self.market_buy_orders_failed_reason1
        stats['market_sell_orders_failed_reason1'] = self.market_sell_orders_failed_reason1
        return stats

    def print_run_stats(self):
        for key, value in self.run_stats_dict().items():
            print("{}={}".format(key, value))
        if len(self.pending_limit_buy_orders) > 0:
            print(self.pending_limit_buy_orders)

    def html_run_stats(self):
        results = str('<br><b>OrderHandler Stats:</b><br>')
        for key, value in self.run_stats_dict().items():
            results += "{}: {}<br>".format(key, value)

        return results

    def round_base(self, price):
        return self.accnt.round_base(price)

    def round_quote(self, price):
        return self.accnt.round_quote(price)

    def update_market_price(self, market_price):
        self.market_price = market_price
        self.accnt.set_market_price(market_price)

    def cancel_order(self, order_id):
        return self.accnt.cancel_order(order_id)

    def cancel_buy_orders(self):
        if len(self.pending_limit_buy_orders) > 0:
            self.accnt.cancel_all()
            self.limit_buy_orders_canceled += len(self.pending_limit_buy_orders)
            self.pending_limit_buy_orders = []
            self.orders_canceled += 1

    def cancel_sell_orders(self):
        if len(self.pending_limit_sell_orders) > 0:
            self.accnt.cancel_all()
            self.orders_canceled += 1
            self.limit_sell_orders_canceled += len(self.pending_limit_sell_orders)
            self.pending_limit_sell_orders = []

    def cancel_last_buy_order(self):
        if len(self.pending_limit_buy_orders) > 0:
            self.pending_limit_buy_orders  = self.pending_limit_buy_orders[1:]

    def cancel_last_sell_order(self):
        if len(self.pending_limit_buy_orders) > 0:
            self.pending_limit_sell_orders = self.pending_limit_sell_orders[1:]

    def cancel_all(self):
        self.accnt.cancel_all()
        self.limit_buy_orders_canceled += len(self.pending_limit_buy_orders)
        self.limit_sell_orders_canceled += len(self.pending_limit_sell_orders)
        self.pending_limit_buy_orders = []
        self.pending_limit_sell_orders = []

    def buy_market(self, price, size):
        usd_value = self.round_quote(price * size)
        if usd_value > self.accnt.quote_currency_available:
            self.market_buy_orders_failed_reason1 += 1
            return False
        self.accnt.set_market_price(price)
        return self.accnt.buy_market(size)

    def sell_market(self, price, size):
        if size < self.accnt.funds_available:
            self.market_sell_orders_failed_reason1 += 1
            return False
        self.accnt.set_market_price(price)
        return self.accnt.sell_market(size)

    # check requirements for order to be successfully added to pending buy orders
    def buy_limit_check(self, price, size):
        amount = self.round_quote(price * size)
        # This should never happen
        if self.accnt.quote_currency_balance < self.accnt.quote_currency_available:
            print("an error has occured in buy_limit_check(), exiting")
            sys.exit(-1)
        if amount > self.accnt.quote_currency_available:
            self.limit_buy_orders_failed_reason1 += 1
            return 1
        if price in self.buy_price_list:
            self.limit_buy_orders_failed_reason2 += 1
            return 2
        #if len(self.sell_price_list) != 0 and price > (min(self.sell_price_list)):
        #    return 2
        #if self.count_4hr > 200:
        #    self.low_4hr, self.high_4hr = self.accnt.get_4hr_stats()
        #    self.count_4hr = 0
        #med = (self.low_4hr + self.high_4hr) / 2.0
        #if price >= med:
        #    return 2
        if amount < 0.01:
            self.limit_buy_orders_failed_reason3 += 1
            return 3
        if price in self.pending_buy_price_list or price in self.buy_price_list:
            self.limit_buy_orders_failed_reason4 += 1
            return 4
        step = self.accnt.min_market_funds
        if self.accnt.currency == 'BTC':
            step = self.accnt.quote_increment
        # use min_market_funds as "spread separator"
        for buy_price in self.pending_buy_price_list:
            if price <= (buy_price + step) and price > (buy_price - step):
                self.limit_buy_orders_failed_reason4 += 1
                return 4
        return 0

    # check requirements for order to be successfully added to pending sell orders
    def sell_limit_check(self, price, size):
        amount = size
        # This should never happen
        #if self.accnt.balance < self.accnt.funds_available:
        #    print("an error has occured in sell_limit_check(): {} {}, exiting".format(self.accnt.balance, self.accnt.funds_available))
        #    sys.exit(-1)
        step = self.accnt.min_market_funds
        if self.accnt.currency == 'BTC':
            step = self.accnt.quote_increment

        if amount > self.accnt.funds_available:
            self.limit_sell_orders_failed_reason1 += 1
            return 1
        if len(self.buy_price_list) == 0 or price < (min(self.buy_price_list) + step):
            self.limit_sell_orders_failed_reason2 += 1
            return 2
        if self.get_lowest_buy_price(price) == 0.0:
            return 2
        if self.last_sell_price != 0.0 and price < self.last_sell_price - step: #* 10:
            return 2
        if amount < self.base_min_size:
            self.limit_sell_orders_failed_reason3 += 1
            return 3
        if price in self.pending_sell_price_list:
            self.limit_sell_orders_failed_reason4 += 1
            return 4

        # use min_market_funds as "spread separator"
        for sell_price in self.pending_sell_price_list:
            if price >= (sell_price - step) and price < (sell_price + step):
                self.limit_sell_orders_failed_reason4 += 1
                return 4
        return 0

    # place buy limit order and place into buy order processing queue
    def buy_limit(self, price, size, post_only=True):
        self.limit_buy_orders_placed += 1
        self.accnt.get_account_balance()
        result = self.buy_limit_check(price, size)

        if result != 0:
            return result

        price = self.round_quote(price)
        result = self.accnt.buy_limit(price, size, post_only)
        if 'id' in result:
            order_id = result['id']
        else:
            print(result)
            order_id = str(uuid.uuid4())

        self.pending_limit_buy_orders.append((price, self.round_base(size), order_id))
        self.pending_buy_price_list.append(price)

        self.limit_buy_orders_pending_count += 1

        # keep track of minimum and maxmimum pending buy price
        if len(self.pending_buy_price_list) == 1:
            self.min_pending_buy_price = price
            self.max_pending_buy_price = price
        elif price > self.max_pending_buy_price:
            self.max_pending_buy_price = price
        elif price < self.min_pending_buy_price:
            self.min_pending_buy_price = price

        currency_available = self.accnt.quote_currency_available - self.round_quote(price * size)
        self.accnt.update_account_balance( self.accnt.quote_currency_balance, currency_available,
                                           self.accnt.balance, self.accnt.funds_available)

    # place sell limit order and put into sell order processing queue
    def sell_limit(self, price, size, post_only=True):
        self.limit_sell_orders_placed += 1
        self.accnt.get_account_balance()

        result = self.sell_limit_check(price, size)
        if result != 0:
            return result

        price = self.round_quote(price)
        result = self.accnt.sell_limit(price, size, post_only)
        if 'id' in result:
            order_id = result['id']
        else:
            print(result)
            order_id = str(uuid.uuid4())
        self.pending_limit_sell_orders.append((price, self.round_base(size), order_id))
        self.pending_sell_price_list.append(price)

        self.limit_sell_orders_pending_count += 1

        # keep track of minimum and maxmimum pending sell price
        if len(self.pending_sell_price_list) == 1:
            self.min_pending_sell_price = price
            self.max_pending_sell_price = price
        elif price > self.max_pending_sell_price:
            self.max_pending_sell_price = price
        elif price < self.min_pending_sell_price:
            self.min_pending_sell_price = price

        funds_available = self.accnt.funds_available - size
        self.accnt.update_account_balance(self.accnt.quote_currency_balance, self.accnt.quote_currency_available,
                                          self.accnt.balance, funds_available)

    # find lowest buy price that sell price is greater than
    def get_lowest_buy_price(self, order_price):
        if len(self.buy_price_list) == 0: return 0.0
        lowest_price = float(self.buy_price_list[0])
        for i in range(1, len(self.buy_price_list)):
            if float(order_price) > float(self.buy_price_list[i]):
                lowest_price = self.buy_price_list[i]

        # sell for at least one tick up from minimum buy price
        if order_price <= (lowest_price + self.accnt.quote_increment * 5):
            self.limit_sell_order_price_too_low += 1
            return 0.0
        return lowest_price

    def process_buy_limit_orders(self, price):
        if price > self.max_pending_buy_price:
            return

        for order in self.pending_limit_buy_orders:
            if len(order) != 3: continue
            order_price = order[0]
            order_size = order[1]
            order_id = order[2]

            # if the price is decreasing and passes order_price, then limit buy order completed
            if price < order_price and not self.accnt.simulation:
                self.accnt.get_account_balance()
                result = self.accnt.get_order(order_id)
                if 'status' in result and ('done_reason' not in result or result['done_reason'] != 'filled'):
                    print("canceled %s %s @ price=%s (%s balance=%f, %s balance=%f)" % (
                        order_size,
                        self.accnt.base_currency,
                        order_price,
                        self.accnt.currency,
                        self.accnt.quote_currency_balance,
                        self.accnt.base_currency,
                        self.accnt.balance,))
                    print(result)

                    if order_price in self.pending_buy_price_list:
                        self.pending_buy_price_list.remove(order_price)
                    if order in self.pending_limit_buy_orders:
                        self.pending_limit_buy_orders.remove(order)
                    return
                else:
                    print(result)
                self.accnt.handle_buy_completed(order_price, order_size)

                if order_price in self.pending_buy_price_list:
                    self.pending_buy_price_list.remove(order_price)
                if order in self.pending_limit_buy_orders:
                    self.pending_limit_buy_orders.remove(order)

                self.buy_price_list.append(order_price)
                self.buy_price_list.sort()

                if len(self.pending_buy_price_list) > 0:
                    self.min_pending_buy_price = self.pending_buy_price_list[0]
                    self.max_pending_buy_price = self.pending_buy_price_list[-1]

                self.last_buy_price = order_price
                self.accnt.get_account_balance()
                total = self.round_quote(price * self.accnt.balance + self.accnt.quote_currency_balance)
                available = price * self.accnt.funds_available + self.accnt.quote_currency_available

                completed_total = self.orders_completed_balance(price)
                print("bought %s %s @ price=%s (%s balance=%f, %s balance=%f, total=%f, completed_total=%f)" % (
                    order_size,
                    self.accnt.base_currency,
                    order_price,
                    self.accnt.currency,
                    self.accnt.quote_currency_balance,
                    self.accnt.base_currency,
                    self.accnt.balance,
                    total,
                    completed_total))

    def process_sell_limit_orders(self, price):
        if price < self.min_pending_sell_price:
            return

        for order in self.pending_limit_sell_orders:
            if len(order) != 3: continue
            order_price = order[0]
            order_size = order[1]
            order_id = order[2]

            # if the price is increasing and passes order_price, then limit sell order completed
            if price > order_price and not self.accnt.simulation:
                self.accnt.get_account_balance()
                result = self.accnt.get_order(order_id)
                if 'status' in result and ('done_reason' not in result or result['done_reason'] != 'filled'):
                    print("canceled %s %s @ price=%s (%s balance=%f, %s balance=%f)" % (
                        order_size,
                        self.accnt.base_currency,
                        order_price,
                        self.accnt.currency,
                        self.accnt.quote_currency_balance,
                        self.accnt.base_currency,
                        self.accnt.balance))

                    if order_price in self.pending_sell_price_list:
                        self.pending_sell_price_list.remove(order_price)
                    if order in self.pending_limit_sell_orders:
                        self.pending_limit_sell_orders.remove(order)
                    return
                else:
                    print(result)
                # find the highest buy price that is less than the sell price, and remove from buy_price_list
                lowest_price = self.get_lowest_buy_price(order_price)
                if lowest_price == 0.0: continue
                self.buy_price_list.remove(lowest_price)

                self.accnt.handle_sell_completed(order_price, order_size)
                if order_price in self.pending_sell_price_list:
                    self.pending_sell_price_list.remove(order_price)
                if order in self.pending_limit_sell_orders:
                    self.pending_limit_sell_orders.remove(order)

                if len(self.pending_sell_price_list) > 0:
                    self.min_pending_sell_price = self.pending_sell_price_list[0]
                    self.max_pending_sell_price = self.pending_sell_price_list[-1]

                self.last_sell_price = order_price
                self.sell_price_list.append(order_price)

                self.accnt.get_account_balance()
                total = self.round_quote(price * self.accnt.balance + self.accnt.quote_currency_balance)


                completed_total = self.orders_completed_balance(price)
                print("sold %s %s @ price=%s (%s balance=%f, %s balance=%f, total=%f, completed_total=%f)" % (
                    order_size,
                    self.accnt.base_currency,
                    order_price,
                    self.accnt.currency,
                    self.accnt.quote_currency_balance,
                    self.accnt.base_currency,
                    self.accnt.balance,
                    total,
                    completed_total))


    def process_limit_orders(self, price):
        if len(self.pending_limit_buy_orders) > 0:
            self.process_buy_limit_orders(price)

        if len(self.pending_limit_sell_orders) > 0:
            self.process_sell_limit_orders(price)

    def refresh_orders(self):
        for order in self.pending_limit_buy_orders:
            return

    # calculate what the total account balance in base currency would be if all open orders completed:
    def orders_completed_balance(self, market_price):
        buy_total = 0.0
        sell_total = 0.0

        for order in self.pending_limit_buy_orders:
            if len(order) != 2: continue
            order_price = float(order[0])
            order_size = float(order[1])
            buy_total += order_price * order_size

        for order in self.pending_limit_sell_orders:
            if len(order) != 2: continue
            order_price = float(order[0])
            order_size = float(order[1])
            sell_total += order_price * order_size

        available = market_price * self.accnt.funds_available + self.accnt.quote_currency_available

        return available + self.round_quote(buy_total) + self.round_quote(sell_total)
