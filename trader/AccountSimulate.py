from trader import AccountBase
from trader import gdax

class AccountSimulate(AccountBase):
    def __init__(self, auth_client, name, currency='USD'):
        self.quote_currency_balance = 0.0
        self.quote_currency_available = 0.0
        self.balance = 0.0
        self.funds_available = 0.0
        self.market_price = 0.0
        self.market_fee = 0.0015 #0.0025
        self.base_currency = name
        self.currency = currency
        self.pending_limit_buy_orders = {}
        self.pending_limit_sell_orders = {}
        self.buy_price = 0.0
        self.buy_price_list = []
        self.ticker_id = ('%s-%s' % (self.base_currency, self.currency))
        self.set_balance(1000.0)
        self.high_24hr = 0.0
        self.low_24hr = 0.0
        self.open_24hr = 0.0
        self.close_24hr = 0.0

        pc = gdax.PublicClient()
        for product in pc.get_products():
            print(product)
            if 'id' in product and product['id'] == self.ticker_id:
                self.quote_increment = float(product['quote_increment'])
                self.base_min_size = float(product['base_min_size'])
                self.min_market_funds = float(product['min_market_funds'])
                break

    def html_run_stats(self):
        results = str('<br><b>Account Stats:</b><br>')
        results += "quote_currency_balance: {}<br>".format(round(self.quote_currency_balance,2))
        results += "quote_currency_available: {}<br>".format(round(self.quote_currency_available,2))
        results += "balance: {}<br>".format(round(self.balance,4))
        results += "funds_available: {}<br>".format(round(self.funds_available,4))
        results += ("high: %f low: %f<br>" % (self.high_24hr, self.low_24hr))
        results += ("open: %f close: %f<br>" % (self.open_24hr, self.close_24hr))
        return results

    def round_base(self, price):
        return round(price, len(str(self.base_min_size)) - 2)

    def round_quote(self, price):
        return round(price, len(str(self.quote_increment)) - 2)

    def update_24hr_stats(self):
        pass

    def handle_buy_completed(self, order_price, order_size):
        self.quote_currency_balance -= self.round_quote(order_price * order_size)
        self.balance += order_size
        self.funds_available += order_size

    def handle_sell_completed(self, order_price, order_size):
        usd_value = self.round_quote(order_price * order_size)
        self.quote_currency_available += usd_value
        self.quote_currency_balance += usd_value
        self.balance -= order_size

    def get_account_balance(self):
        pass

    def update_account_balance(self, currency_balance, currency_available, balance, available):
        #print("Updated quote_currency_available from {} to {}".format(self.quote_currency_available, currency_available))
        self.quote_currency_available = currency_available
        self.quote_currency_balance = currency_balance
        self.balance = balance
        self.funds_available = available

    def set_balance(self, balance_usd):
        self.quote_currency_balance = balance_usd
        self.quote_currency_available = balance_usd

    def set_market_price(self, price):
        self.market_price = price

    def fee(self, price, size):
        value_usd = price * size
        return self.round_quote(value_usd * self.market_fee)

    def buy_market(self, size):
        funds_available = self.round_base(self.funds_available)
        size = self.round_base(size)
        usd_value = self.round_quote(self.market_price * size)
        print("buy_market({}, {}), available BTC={}, usd_value={}".format(self.market_price, size, funds_available, usd_value))
        if self.quote_currency_available >= usd_value:
            self.quote_currency_available -= usd_value # - self.fee(self.market_price, size)
            self.quote_currency_balance -= usd_value # - self.fee(self.market_price, size)
            self.funds_available += size
            self.balance += size

            total = self.market_price * self.balance+ self.quote_currency_balance
            print("bought %s BTC @ price=%s (USD balance=%f, BTC balance=%f, total=%f)" % (
                size, self.market_price, self.quote_currency_balance, self.balance, total))
            return True
        return False

    def sell_market(self, size):
        funds_available = self.round_base(self.funds_available)
        size = self.round_base(size)
        usd_value = self.round_quote(self.market_price * size)
        print("sell_market({}, {}), available BTC={}, usd_value={}".format(self.market_price, size, funds_available, usd_value))
        if funds_available >= size:
            self.quote_currency_available += usd_value #- 2 * self.fee(self.market_price, size)
            self.quote_currency_balance += usd_value #- 2 * self.fee(self.market_price, size)
            self.funds_available -= size
            self.balance -= size
            total = self.market_price * self.balance + self.quote_currency_balance
            print("sold %s BTC @ price=%s (USD balance=%f, BTC balance=%f, total=%f)" % (
                size, self.market_price, self.quote_currency_balance, self.balance, total))
            return True
        return False

    def buy_limit(self, price, size, post_only=True):
        #if len(self.pending_limit_buy_orders) == 0: return
        price = self.round_quote(price)
        size = self.round_base(size)
        #for buy_price in self.buy_price_list:
        #    if price > 1.0 and int(float(price)) == int(float(buy_price)): return
        usd_value = self.round_quote(self.market_price * size)
        if usd_value <= 0.0: return
        if self.quote_currency_available >= usd_value:
            #print("pending buy {} @ {} balance={} available={}".format(price, size, self.quote_currency_balance, self.quote_currency_available))
            self.quote_currency_available -= usd_value
            return True
            #self.pending_limit_buy_orders[str(price)] = size
        return False

    def sell_limit(self, price, size, post_only=True):
        price = self.round_quote(price)
        size = self.round_base(size)
        #if len(self.pending_limit_sell_orders) > 0: return
        if size < self.base_min_size: return False
        if self.funds_available >= size:
            #print("pending sell {} @ {} balance={} available={}".format(price, size, self.balance, self.funds_available))
            self.funds_available -= size
            #self.pending_limit_sell_orders[str(price)] = size
            return True
        return False

    def process_limit_orders(self, price):
        # handle buy orders
        for order_price, order_size in self.pending_limit_buy_orders.items():
            if order_price >= price:
                self.quote_currency_balance = self.quote_currency_available
                self.balance += order_size
                self.funds_available = self.balance
                total = price * self.balance + self.quote_currency_balance
                del self.pending_limit_buy_orders[order_price]
                self.buy_price_list.append(order_price)
                #self.buy_price = order_price
                print("bought %s BTC @ price=%s (USD balance=%f, BTC balance=%f, total=%f)" % (
                    order_size, order_price, self.quote_currency_balance, self.balance, total))
        if len(self.pending_limit_sell_orders) == 0: return
        # handle sell orders
        for order_price, order_size in self.pending_limit_sell_orders.items():
            if order_price <= price and len(self.buy_price_list) > 0:
                # find lowest buy price that sell price is greater than
                lowest_price = float(self.buy_price_list[0])
                for i in range(1, len(self.buy_price_list)):
                    if float(order_price) > float(self.buy_price_list[i]):
                        lowest_price = self.buy_price_list[i]
                if order_price < lowest_price: break
                self.buy_price_list.remove(lowest_price)

                usd_value = self.round_quote(order_price * order_size)
                self.quote_currency_available += usd_value
                self.quote_currency_balance  += usd_value
                self.balance = self.funds_available
                total = price * self.balance + self.quote_currency_balance
                self.pending_limit_sell_orders.remove([order_price, order_size])
                del self.pending_limit_sell_orders[order_price]
                #self.buy_price = 0.0
                print("sold %s BTC @ price=%s (USD balance=%f, BTC balance=%f, total=%f)" % (
                    order_size, order_price, self.quote_currency_balance, self.balance, total))


    def get_account_history(self):
        pass

    def get_price(self):
        pass

    def set_market_price(self, market_price):
        self.market_price = market_price

    def get_account_history(self):
        pass

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        pass

    def get_order(self, order_id):
        pass

    def get_orders(self):
        pass

    def buy_limit_stop(self, price, size, stop_price, post_only=True):
        pass

    def sell_limit_stop(self, price, size, stop_price, post_only=True):
        pass

    def cancel_order(self, order_id):
        pass

    def cancel_all(self):
        pass
