from trader import AccountBase
from trader.myhelpers import *
from datetime import timedelta, datetime
import aniso8601
import numpy as np

def datetime_to_float(d):
    epoch = datetime.utcfromtimestamp(0)
    total_seconds =  (d.replace(tzinfo=None) - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return float(total_seconds)

class AccountGDAX(AccountBase):
    def __init__(self, auth_client, name, currency='USD', simulation=False):
        self.account_type = 'GDAX'
        self.simulation = simulation
        self.quote_currency_balance = 0.0
        self.quote_currency_available = 0.0

        for account in auth_client.get_accounts():
            if 'currency' not in account: continue

            if account['currency'] == currency:
                self.quote_currency_balance = float(account['balance'])
                self.quote_currency_available = float(account['available'])
                continue

            if 'currency' not in account or account['currency'] != name: continue

            self.auth_client = auth_client
            self.account_id = account['id']
            self.profile_id = account['profile_id']
            self.base_currency = account['currency']
            self.currency = currency
            self.ticker_id = self.get_ticker_id()
            self.balance = float(account['balance'])
            self.funds_available = float(account['available'])

        self.pc = gdax.PublicClient()
        for product in self.pc.get_products():
            if 'id' in product and product['id'] == self.ticker_id:
                self.quote_increment = float(product['quote_increment'])
                self.base_min_size = float(product['base_min_size'])
                self.min_market_funds = float(product['min_market_funds'])
                break

        print("{}-{}".format(name, currency))
        print("min_market_funds={}".format(self.min_market_funds))
        print("base_min_size={}".format(self.base_min_size))
        print("quote_increment={}".format(self.quote_increment))
        self.high_24hr = self.low_24hr = 0.0
        self.open_24hr = self.close_24hr = self.volume_24hr = 0.0
        self.update_24hr_stats()

        if self.simulation:
            print("Simulation mode enabled")

    def check_order_error(self, result, side):
        if 'message' in result and (result['message'] == 'Insufficient funds'
                                    or result['message'] == 'Internal server error'
                                    or result['message'].startswith('size is too small.')
                                    or result['message'] == 'Invalid post_only true'
                                    or result['message'] == 'request timestamp expired'):
            return True
        elif 'status' in result and (result['status'] == 'rejected'):
            return True
        return False

    def html_run_stats(self):
        results = str('')
        results += "quote_currency_balance: {}<br>".format(self.quote_currency_balance)
        results += "quote_currency_available: {}<br>".format(self.quote_currency_available)
        results += "balance: {}<br>".format(self.balance)
        results += "funds_available: {}<br>".format(self.funds_available)
        results += ("high: %f low: %f open: %f<br>" % (self.high_24hr, self.low_24hr, self.open_24hr))
        return results

    def round_base(self, price):
        return round(price, '{:f}'.format(self.base_min_size).index('1') - 1)

    def round_quote(self, price):
        return round(price, '{:f}'.format(self.quote_increment).index('1') - 1)

    def update_24hr_stats(self):
        stats = self.pc.get_product_24hr_stats(self.ticker_id)
        self.high_24hr = float(stats['high'])
        self.low_24hr = float(stats['low'])
        self.open_24hr = float(stats['open'])
        self.close_24hr = float(stats['last'])
        self.volume_24hr = float(stats['volume'])

    def get_4hr_stats(self):
        klines = retrieve_klines_last_hour(self.ticker_id, hours=4)
        low = 0.0
        high = 0.0
        for kline in klines:
            if low == 0.0:
                low = float(kline[1])
            else:
                if float(kline[1]) < low: low = float(kline[1])
            if float(kline[2]) > high: high = float(kline[2])
        return low, high

    # preload buy_price_list from GDAX account
    def preload_buy_price_list(self):
        buy_price_list = []
        sell_price_list = []
        if self.balance < self.base_min_size:
            return buy_price_list, sell_price_list
        max_buy_price = 0.0
        buy_price_found = False
        base_amount = 0.0
        sell_counter = 0.0
        for fill in self.get_fills(product_id=self.ticker_id)[0]:
            if base_amount >= self.balance and self.balance < self.base_min_size:
                break
            if len(fill) != 0 and 'side' in fill and fill['side'] == 'buy':
                if sell_counter > 0.0:
                    sell_counter -= float(fill['size'])
                    continue
                if float(fill['price']) in buy_price_list: continue
                if float(fill['price']) > max_buy_price:
                    max_buy_price = float(fill['price'])
                buy_price_found = True
                buy_price_list.append(float(fill['price']))
                base_amount += float(fill['size'])
            elif len(fill) != 0 and 'side' in fill and fill['side'] == 'sell':
                sell_counter += float(fill['size'])
                sell_price_list.append(float(fill['price']))
        if len(buy_price_list) > 2:
            buy_price_list.sort()
            #buy_price_list = buy_price_list[1:]

        sell_price_list.sort()

        return buy_price_list, sell_price_list

    def get_ticker_id(self):
        return '%s-%s' % (self.base_currency, self.currency)

    def get_deposit_address(self):
        return self.auth_client.get_deposit_address(self.get_ticker_id())

    def handle_buy_completed(self, price, size):
        pass

    def handle_sell_completed(self, price, size):
        pass

    def get_account_history(self):
        return self.auth_client.get_account_history(account_id=self.account_id)

    def update_account_balance(self, currency_balance, currency_available, balance, available):
        self.get_account_balance()

    def get_account_balance(self):
        for account in self.auth_client.get_accounts():
            if 'currency' not in account: continue

            if account['currency'] == self.currency:
                self.quote_currency_balance = self.round_quote(float(account['balance']))
                self.quote_currency_available = self.round_quote(float(account['available']))
                continue
            elif account['currency'] == self.base_currency:
                self.balance = self.round_base(float(account['balance']))
                self.funds_available = self.round_base(float(account['available']))
                continue

        return {"base_balance": self.balance, "base_available": self.funds_available,
                "quote_balance": self.quote_currency_balance, "quote_available": self.quote_currency_available}

    def get_price(self):
        ticker= gdax.PublicClient().get_product_ticker(product_id=self.ticker_id)
        return (float(ticker['bid']) + float(ticker['ask'])) / 2.0

    def set_market_price(self, price):
        pass

    def get_fill(self, order_id=''):
        return self.auth_client.get_fills(order_id=order_id)

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        return self.auth_client.get_fills(order_id, product_id, before, after, limit)

    def get_order(self, order_id):
        return self.auth_client.get_order(order_id=order_id)

    def get_orders(self):
        return self.auth_client.get_orders(product_id=self.ticker_id)

    def get_open_buy_orders(self):
        result = []
        orders = self.get_orders()
        if not orders or len(orders[0]) == 0: return result
        for order in orders[0]:
            if 'side' not in order: continue
            if order['side'] == 'buy' and 'price' in order and 'size' in order:
                result.append([float(order['price']), float(order['size'])])
        return result

    def get_open_sell_orders(self):
        result = []
        orders = self.get_orders()
        if not orders or len(orders[0]) == 0: return result
        for order in orders[0]:
            if 'side' not in order: continue
            if order['side'] == 'sell' and 'price' in order and 'size' in order:
                result.append([float(order['price']), float(order['size'])])
        return result

    def buy_limit_stop(self, price, size, stop_price, post_only=True):
        return self.auth_client.buy(price=price, size=size, product_id=self.ticker_id,
                                    type='limit', post_only=post_only, stop='entry', stop_price=stop_price)

    def buy_limit(self, price, size, post_only=True):
        print("buy_limit({}, {})".format(price, size))
        if self.simulation:
            return
        result =  self.auth_client.buy(price=price, size=size, product_id=self.ticker_id,
                                    type='limit', post_only=post_only)

        if 'message' in result and result['message'].startswith('size is too small'):
            self.cancel_all()
            size = self.base_min_size = 0.01
            result = self.buy_limit(price, size, post_only)
            print('set base_min_size=0.01')
        return result

    def buy_market(self, size):
        return self.auth_client.buy(size=size, product_id=self.ticker_id, type='market')

    def sell_limit_stop(self, price, size, stop_price, post_only=True):
        return self.auth_client.sell(price=price, size=size, product_id=self.ticker_id,
                                     type='limit', post_only=post_only, stop='loss', stop_price=stop_price)

    def sell_limit(self, price, size, post_only=True):
        print("sell_limit({}, {})".format(price, size))
        if self.simulation:
            return
        return self.auth_client.sell(price=price, size=size, product_id=self.ticker_id,
                                     type='limit', post_only=post_only)

    def sell_market(self, size):
        return self.auth_client.sell(size=size, product_id=self.ticker_id, type='market')

    def cancel_order(self, order_id):
        return self.auth_client.cancel_order(order_id=order_id)

    def cancel_all(self):
        return self.auth_client.cancel_all(product_id=self.ticker_id)

    def query_price_last_hour(self):
        x = []
        y = []
        end = datetime.utcnow()
        start = (end - timedelta(hours=1))
        result = self.collection.find({"type": "match", "time": {"$gt": start.isoformat(), "$lte": end.isoformat()}},
                                        {"time": 1, "price": 1, "_id": False})
        for ent in result:
            x.append(datetime_to_float(aniso8601.parse_datetime(ent['time'])))
            y.append(float(ent['price']))
        return {"x": x, "y": y}

    def query_price_last_day(self):
        x = []
        y = []
        end = datetime.utcnow()
        start = (end - timedelta(days=1))
        result = self.collection.find({"type": "match", "time": {"$gt": start.isoformat(), "$lte": end.isoformat()}},
                                        {"time": 1, "price": 1, "_id": False})
        for ent in result:
            x.append(aniso8601.parse_datetime(ent['time']).replace(tzinfo=None))
            y.append(float(ent['price']))
        return {"x": x, "y": y}

    def compute_sma_from_prices(self, data, window=12):
        sma = []
        prices = []
        age = 0
        sum = 0.0

        for i in range(0, len(data) - 1):
            if len(prices) < window:
                tail = 0  # float(data[i])
                prices.append(float(data[i]))
            else:
                tail = prices[age]
                prices[age] = float(data[i])
            sum += float(data[i]) - tail
            sma.append(sum / float(len(prices)))
            age = (age + 1) % window
        return sma

    def compute_ema_from_prices(self, data, weight=26):
        ema = []
        prices = self.compute_sma_from_prices(data, weight)
        k = 2.0 / (float(weight) * 24.0 + 1.0)
        last_price = float(prices[0])

        for i in range(1, len(prices) - 1):
            last_price = float(prices[i] * k + last_price * (1.0 - k))
            ema.append(last_price)
        return ema

    def compute_smma_from_prices(self, data, weight=14):
        smma = []
        sma = self.compute_sma_from_prices(data, weight)

        result = sma[0]
        for i in range(1, len(sma) - 1):
            value = sma[i]
            result = (result * (weight - 1.0) + value) / weight
            smma.append(result)
        return smma

    def compute_ema_last_hour(self, weight=26):
        prices = self.query_price_last_hour()
        ema = self.compute_ema_from_prices(prices["y"], weight)
        return {"x": prices["x"], "y": ema}

    def compute_smma_last_hour(self, weight=14):
        prices = self.query_price_last_hour()
        smma = self.compute_smma_from_prices(prices["y"], weight)
        offset = len(prices["x"]) - len(smma)
        return {"x": prices["x"][offset:], "y": smma}

    def compute_ema_crossover(self, prices, ema1, ema2):
        if len(ema2["y"]) < len(ema1["y"]):
            ema1["y"] = ema1["y"][0:len(ema2["y"])]
        elif len(ema2["y"]) > len(ema1["y"]):
            ema2["y"] = ema2["y"][0:len(ema1["y"])]
        ema1prices = np.array(ema1["y"])
        ema2prices = np.array(ema2["y"])
        mask = ema1prices > ema2prices

        crossovers = []

        unit_price = float(len(prices["x"])) / (max(prices["y"]) - min(prices["y"]))

        for i in range(0, len(mask) - 2):
            if mask[i] and not mask[i + 1]:
                slopex = ema1["x"][i + 2] - ema1["x"][i - 2]
                slope1 = 0.0
                slope2 = 0.0
                if slopex != 0.0:
                    slope1 = unit_price * (float(ema1prices[i + 2]) - float(ema1prices[i - 2])) / slopex
                    slope2 = unit_price * (float(ema2prices[i + 2]) - float(ema2prices[i - 2])) / slopex

                now = datetime_to_float(datetime.utcnow())
                time_ago = int(now - ema1["x"][i])
                crossovers.append([i, time_ago, slope1, slope2])
            elif not mask[i] and mask[i + 1]:
                slopex = ema1["x"][i + 2] - ema1["x"][i - 2]
                slope1 = 0.0
                slope2 = 0.0
                if slopex != 0.0:
                    slope1 = unit_price * (float(ema1prices[i + 2]) - float(ema1prices[i - 2])) / slopex
                    slope2 = unit_price * (float(ema2prices[i + 2]) - float(ema2prices[i - 2])) / slopex

                now = datetime_to_float(datetime.utcnow())
                time_ago = int(now - ema1["x"][i])
                crossovers.append([i, time_ago, slope1, slope2])
        return crossovers

    def compute_ema_slope_changes(self, prices, ema):
        unit_price = float(len(prices["x"])) / (max(prices["y"]) - min(prices["y"]))
        emaprices = np.array(ema["y"])
        slopes = []

        for offset in range(1, 2):
            for i in range(0, len(emaprices) - offset):
                slopex = float(ema["x"][i + offset] - ema["x"][i])
                if slopex == 0.0: continue
                slope = unit_price * (float(emaprices[i + offset]) - float(emaprices[i])) / slopex
                if slope != 0.0: # and (slope > 0.001 or slope < -0.001):
                    slopes.append([i + offset, slope])
            if len(slopes) > 0: break

        slope_ranges = []

        positive_range_start = -1
        negative_range_start = -1

        for i in range(0, len(slopes)):
            if positive_range_start == -1 and negative_range_start == -1:
                if slopes[i][1] > 0.0: positive_range_start = i
                if slopes[i][1] < 0.0: negative_range_start = i
            elif positive_range_start == -1 and negative_range_start != -1:
                if slopes[i][1] > 0.0:
                    #if (i - negative_range_start) > 10:
                    slope_ranges.append([negative_range_start, i, -1])
                    positive_range_start = i
                    negative_range_start = -1
            elif positive_range_start != -1 and negative_range_start == -1:
                if slopes[i][1] < 0.0:
                    #if (i - positive_range_start) > 5:
                    slope_ranges.append([positive_range_start, i, 1])
                    positive_range_start = -1
                    negative_range_start = i

        #combined_slope_ranges = []
        #i=0
        #while i < (len(slope_ranges) - 1):
        #    if slope_ranges[i][2] == slope_ranges[i+1][2]:
        #        combined_slope_ranges.append([slope_ranges[i][0], slope_ranges[i+1][1], slope_ranges[i][2]])
        #        i += 1
        #    else:
        #        combined_slope_ranges.append(slope_ranges[i])
        #    i += 1
        slope_pivot_points = []

        for i in range(0, len(slope_ranges) - 1):
            if slope_ranges[i][2] == -1 and slope_ranges[i + 1][2] == 1:
                pos = (slope_ranges[i][1] + slope_ranges[i + 1][0]) / 2
                pos = slopes[pos]
                timeval = ema["x"][pos[0]]
                price = round(ema["y"][pos[0]], 4)
                slope_pivot_points.append([timeval, price, 1])
                #print("valley at %d" % pos)
            elif slope_ranges[i][2] == 1 and slope_ranges[i + 1][2] == -1:
                pos = (slope_ranges[i][1] + slope_ranges[i + 1][0]) / 2
                #print("peak at %d" % pos)
                pos = slopes[pos]
                timeval = ema["x"][pos[0]]
                price = ema["y"][pos[0]]
                slope_pivot_points.append([timeval, price, -1])
            else:
                pos = (slope_ranges[i][1] + slope_ranges[i + 1][0]) / 2
                #print("peak at %d" % pos)
                pos = slopes[pos]
                timeval = ema["x"][pos[0]]
                price = round(ema["y"][pos[0]], 4)
                slope_pivot_points.append([timeval, price, 0])
        return slope_pivot_points
        #i = 0
        #while i < (len(slopes) - 1 - 4):
        #    if slopes[i][1] > 0.0 and slopes[i+4][1] < 0.0:
        #        slope_change = True
        #        for j in range(5, 40):
        #            if (i - j) < 0 or (i + j) > (len(slopes) - 1 - 4):
        #                slope_change = False
        #                break
        #            if slopes[i - j][1] < 0.0 or slopes[i + j][1] > 0.0:
        #                slope_change = False
        #                break
        #        if slope_change:
        #            print("peak at %d price=%f" % (slopes[i][0], emaprices[slopes[i][0]]))
        #            i += 4
        #    elif slopes[i][1] < 0.0 and slopes[i+4][1] > 0.0:
        #        slope_change = True
        #        for j in range(5, 40):
        #            if (i - j) < 0 or (i + j) > (len(slopes) - 1 - 4):
        #                slope_change = False
        #                break
        #            if slopes[i - j][1] > 0.0 or slopes[i + j][1] < 0.0:
        #                slope_change = False
        #                break
        #        if slope_change:
        #            print("valley at %d price=%f" % (slopes[i][0], emaprices[slopes[i][0]]))
        #            i += 4
        #    i += 1
