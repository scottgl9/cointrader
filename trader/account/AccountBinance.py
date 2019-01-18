from trader.account.binance.client import Client, BinanceAPIException
from trader.account.AccountBase import AccountBase
from trader.lib.Message import Message
from trader.lib.Order import Order
from trader.lib.AssetInfo import AssetInfo
import json
import os

#logger = logging.getLogger(__name__)

class AccountBinance(AccountBase):
    def __init__(self, client, name='BTC', asset='USD', simulation=False, logger=None, simulate_db_filename=None):
        self.account_type = 'Binance'
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation
        self.info_all_assets = {}
        self.details_all_assets = {}
        self.balances = {}
        if self.simulate:
            self.currencies = ['BTC', 'ETH', 'BNB']
        else:
            self.currencies = ['BTC', 'ETH', 'BNB', 'PAX', 'XRP', 'USDT', 'USDC', 'TUSD']
        self.currency_trade_pairs = ['ETHBTC', 'BNBBTC', 'BNBETH', 'BTCPAX', 'ETHPAX', 'BNBPAX',
                                     'ETHUSDT', 'BTCUSDT', 'BNBUSDT']

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.currencies:
            self._currency_buy_size[currency] = 0

        self.client = client
        self.ticker_id = '{}{}'.format(name, asset)
        #self.info = self.client.get_symbol_info(symbol=self.ticker_id)
        #self.update_24hr_stats()

    def set_market_price(self, price):
        pass

    def get_currencies(self):
        return self.currencies

    def get_currency_trade_pairs(self):
        return self.currency_trade_pairs

    def is_currency(self, name):
        if name in self.currencies:
            return True
        return False

    def is_currency_pair(self, symbol=None, base=None, currency=None):
        if not base or not currency:
            base, currency = self.split_ticker_id(symbol)
        if not base or not currency:
            return False
        if base not in self.currencies:
            return False
        if currency not in self.currencies:
            return False
        return True

    def get_currency_buy_size(self, name):
        if not self.is_currency(name):
            return 0
        return self._currency_buy_size[name]

    def set_currency_buy_size(self, name, size=0):
        if not self.is_currency(name):
            return 0
        self._currency_buy_size[name] = size

    # buy_size is amount of currency used to buy an asset
    # sell_size is amount of currency retrieved by selling asset
    def update_currency_buy_size(self, name, asset_buy_size=0, asset_sell_size=0):
        if not self.is_currency(name):
            return 0
        if asset_buy_size:
            self._currency_buy_size[name] -= asset_buy_size
        if asset_sell_size:
            self._currency_buy_size[name] += asset_sell_size
        return self._currency_buy_size[name]

    def round_base(self, price, base_min_size=0):
        if base_min_size != 0.0:
            return round(price, '{:.9f}'.format(float(base_min_size)).index('1') - 1)
        return price

    def round_quote(self, price, quote_increment=0):
        if quote_increment != 0.0:
            return round(price, '{:.9f}'.format(float(quote_increment)).index('1') - 1)
        return price

    def round_quote_symbol(self, symbol, price):
        quote_increment = self.get_asset_info_dict(symbol=symbol, field='tickSize')
        return self.round_quote(price, quote_increment)

    def round_quote_pair(self, base, currency, price):
        quote_increment = self.get_asset_info_dict(base=base, currency=currency, field='tickSize')
        return self.round_quote(price, quote_increment)

    def my_float(self, value):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            return "{:.9f}".format(float(value))

    def make_ticker_id(self, base, currency):
        return '%s%s' % (base, currency)

    def split_ticker_id(self, symbol):
        base_name = None
        currency_name = None

        for currency in self.currencies:
            if symbol.endswith(currency):
                currency_name = currency
                base_name = symbol.replace(currency, '')
        return base_name, currency_name

    def split_symbol(self, symbol):
        return self.split_ticker_id(symbol)

    def get_detail_all_assets(self):
        return self.client.get_asset_details()

    def get_info_all_assets(self, info_all_assets=None):
        assets = {}

        if not info_all_assets:
            info_all_assets = self.client.get_exchange_info()

        for key, value in info_all_assets.items():
            if key != 'symbols':
                continue
            for asset in value:
                minNotional = ''
                minQty = ''
                minPrice = ''
                tickSize = ''
                stepSize = ''
                commissionAsset = ''
                for filter in asset['filters']:
                    if 'minQty' in filter:
                        minQty = filter['minQty']
                    if 'minPrice' in filter:
                        minPrice = filter['minPrice']
                    if 'tickSize' in filter:
                        tickSize = filter['tickSize']
                    if 'stepSize' in filter:
                        stepSize = filter['stepSize']
                    if 'minNotional' in filter:
                        minNotional = filter['minNotional']
                    if 'commissionAsset' in filter:
                        commissionAsset = filter['commissionAsset']

                assets[asset['symbol']] = {'minQty': minQty,
                                           'minPrice': minPrice,
                                           'tickSize': tickSize,
                                           'stepSize': stepSize,
                                           'minNotional': minNotional,
                                           'commissionAsset': commissionAsset
                                           }

        return assets

    # use get_info_all_assets to load asset info into self.info_all_assets
    def load_info_all_assets(self):
        if not self.simulate:
            self.info_all_assets = self.get_info_all_assets()
            return

        if not os.path.exists("asset_info.json"):
            assets_info = self.client.get_exchange_info()
            with open('asset_info.json', 'w') as f:
                json.dump(assets_info, f, indent=4)
        else:
            assets_info = json.loads(open('asset_info.json').read())
        self.info_all_assets = self.get_info_all_assets(assets_info)

    # use get_info_all_assets to load asset info into self.info_all_assets
    def load_detail_all_assets(self):
        if not self.simulate:
            self.details_all_assets = self.get_detail_all_assets()
            return

        if not os.path.exists("asset_detail.json"):
            self.details_all_assets = self.get_detail_all_assets()
            with open('asset_detail.json', 'w') as f:
                json.dump(self.details_all_assets, f, indent=4)
        else:
            self.details_all_assets = json.loads(open('asset_detail.json').read())

    def get_asset_status(self, name=None):
        if not self.details_all_assets:
            self.load_detail_all_assets()

        result = self.details_all_assets
        if 'assetDetail' in result.keys():
            self.details_all_assets = result['assetDetail']

        if name and name in self.details_all_assets.keys():
            return self.details_all_assets[name]

        return None

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        if not self.info_all_assets:
            self.load_info_all_assets()

        if not symbol:
            symbol = self.make_ticker_id(base, currency)

        if not self.info_all_assets or symbol not in self.info_all_assets.keys():
            return None
        if field:
            if field not in self.info_all_assets[symbol]:
                return None
            return self.info_all_assets[symbol][field]
        return self.info_all_assets[symbol]

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['minQty']
        min_price=info['minPrice']
        base_step_size=info['stepSize']
        currency_step_size=info['tickSize']
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)

        result = AssetInfo(base=base,
                           currency=currency,
                           min_qty=min_qty,
                           min_price=min_price,
                           base_step_size=base_step_size,
                           currency_step_size=currency_step_size,
                           is_currency_pair=is_currency_pair
                           )
        return result

    # parse json response to binance API order, then use to create Order object
    def parse_order_result(self, result, symbol=None):
        fills = None
        orderid = None
        order_type = None
        type = None
        origqty = 0
        quoteqty = 0
        side = None
        commission = 0
        status = None
        prices = []
        type = None
        order_type = None
        symbol = symbol

        if self.simulate:
            return None

        self.logger.info("result={}".format(result))

        if 'orderId' in result: orderid = result['orderId']
        if 'origQty' in result: origqty = result['origQty']
        fills = result['fills']
        if 'cummulativeQuoteQty' in result: quoteqty = float(result['cummulativeQuoteQty'])
        if 'symbol' in result: symbol = result['symbol']
        if 'status' in result: status = result['status']
        if 'type' in result: order_type = result['type']
        if 'side' in result: side = result['side']
        if 'price' in result and float(result['price']) != 0:
            prices.append(float(result['price']))

        for fill in fills:
            if 'side' in fill: side = fill['side']
            if 'type' in fill: order_type = fill['type']
            if 'status' in fill: status = fill['status']
            if 'price' in fill and float(fill['price']) != 0:
                prices.append(float(result['price']))
            if 'type' in fill: order_type = fill['type']
            if 'symbol' in fill: symbol = fill['symbol']
            if 'commission' in fill: commission = fill['commission']

        if not symbol or status != 'FILLED':
            return None

        if not side or not order_type:
            return None

        price = 0
        if len(prices) != 0:
            if side == 'BUY':
                price = max(prices)
            elif side == 'SELL':
                price = min(prices)

        if order_type == 'MARKET' and side == 'BUY':
            type = Message.MSG_MARKET_BUY
        elif order_type == 'MARKET' and side == 'SELL':
            type = Message.MSG_MARKET_SELL
        elif order_type == 'LIMIT' and side == 'BUY':
            type = Message.MSG_LIMIT_BUY
        elif order_type == 'LIMIT' and side == 'SELL':
            type = Message.MSG_LIMIT_SELL
        else:
            return None

        order = Order(symbol=symbol,
                      price=price,
                      size=origqty,
                      type=type,
                      orderid=orderid,
                      quote_size=quoteqty,
                      commission=commission)

        self.logger.info("order: {}".format(str(order)))
        return order

    # determine if asset has disabled deposits, if so don't trade
    def deposit_asset_disabled(self, name):
        status = self.get_asset_status(name)
        if status and 'depositStatus' in status:
            return not status['depositStatus']
        return False

    def get_deposit_address(self, name=None):
        result = self.client.get_deposit_address(asset=name)
        if 'success' in result and 'address' in result and result['success']:
            return result['address']
        return ''

    def get_open_buy_orders(self):
        return []

    def get_open_sell_orders(self):
        return []

    def preload_buy_price_list(self):
        return [], []

    def get_24hr_stats(self, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id

        stats = self.client.get_ticker(symbol=ticker_id)

        high_24hr = low_24hr = 0.0
        open_24hr = last_24hr = 0.0
        volume = 0.0
        ts_24hr = 0

        if 'highPrice' in stats:
            high_24hr = float(stats['highPrice'])
        if 'lowPrice' in stats:
            low_24hr = float(stats['lowPrice'])
        if 'openPrice' in stats:
            open_24hr = float(stats['openPrice'])
        if 'lastPrice' in stats:
            last_24hr = float(stats['lastPrice'])
        if 'volume' in stats:
            volume = float(stats['volume'])
        if 'openTime' in stats:
            ts_24hr = int(stats['openTime'])

        return {'l': low_24hr, 'h': high_24hr, 'o': open_24hr, 'c': last_24hr, 'v': volume, 't': ts_24hr}

    #def get_asset_balance(self, asset):
    #    return self.client.get_asset_balance(asset=asset)

    def get_account_total_value(self):
        btc_usd_price = float(self.client.get_symbol_ticker(symbol='BTCUSDT')['price'])
        tickers = []
        for key, value in self.client.get_exchange_info().items():
            if key != 'symbols': continue
            for asset in value:
                # if asset['symbol'].endswith('USDT'): continue
                tickers.append(asset['symbol'])

        print(btc_usd_price)
        total_balance_usd = 0.0
        total_balance_btc = 0.0
        for accnt in self.client.get_account()['balances']:
            if float(accnt['free']) != 0.0 or float(accnt['locked']) != 0.0:
                price = 0.0
                price_usd = 0.0
                price_btc = 0.0
                if accnt['asset'] != 'BTC' and accnt['asset'] != 'USDT':
                    symbol = "{}BTC".format(accnt['asset'])
                    if symbol not in tickers:
                        continue
                    price = float(self.client.get_symbol_ticker(symbol)['price'])
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = price * total_amount
                elif accnt['asset'] != 'USDT':
                    price = 1.0
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = total_amount
                else:
                    price = 1.0
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = total_amount / btc_usd_price

                price_usd = price_btc * btc_usd_price
                total_balance_usd += price_usd
                total_balance_btc += price_btc
                usd_price = price * btc_usd_price

        return total_balance_usd, total_balance_btc

    def total_btc_available(self, tickers):
        for symbol, price in self.balances.items():
            if symbol != 'BTC':
                ticker_id = "{}BTC".format(symbol)
                if ticker_id not in tickers:
                    return False
        return True

    def get_total_btc_value(self, tickers=None):
        total_balance_btc = 0.0

        if not tickers:
            tickers = {}
            for entry in self.client.get_orderbook_tickers():
                tickers[entry["symbol"]] = float(entry["bidPrice"])

        for symbol, size in self.balances.items():
            size_btc = 0.0
            if symbol == 'BTC':
                size_btc = float(self.balances['BTC']['balance'])
            elif symbol != 'USDT':
                ticker_id = "{}BTC".format(symbol)
                if ticker_id not in tickers.keys():
                    continue
                amount = float(self.balances[symbol]['balance'])

                if isinstance(tickers[ticker_id], float):
                    size_btc = float(tickers[ticker_id]) * amount
                else:
                    size_btc = float(tickers[ticker_id][4]) * amount

            total_balance_btc += size_btc

        return total_balance_btc

    def get_account_status(self):
        return self.client.get_account_status()

    def update_asset_balance(self, name, balance, available):
        if self.simulate:
            if name in self.balances.keys() and balance == 0.0 and available == 0.0:
                del self.balances[name]
                return
            if name not in self.balances.keys():
                self.balances[name] = {}
            self.balances[name]['balance'] = balance
            self.balances[name]['available'] = available

    def get_account_balances(self):
        self.balances = {}
        result = {}
        for funds in self.client.get_account()['balances']:
            funds_free = float(funds['free'])
            funds_locked = float(funds['locked'])
            if funds_free == 0.0 and funds_locked == 0.0: continue
            asset_name = funds['asset']
            self.balances[asset_name] = {'balance': (funds_free + funds_locked), 'available': funds_free}
            result[asset_name] = funds_free + funds_locked
        return result

    def get_asset_balance(self, asset):
        if asset in self.balances.keys():
            return self.balances[asset]
        return {'balance': 0.0, 'available': 0.0}

    def get_asset_balance_tuple(self, asset):
        result = self.get_asset_balance(asset)
        if 'balance' not in result or 'available' not in result:
            return 0.0, 0.0
        return float(result['balance']), float(result['available'])

    def get_deposit_history(self, asset=None):
        return self.client.get_deposit_history(asset=asset)

    def get_all_tickers(self):
        result = []
        for ticker in self.client.get_all_tickers():
            result.append(ticker['symbol'])
        return result

    def get_all_my_trades(self, limit=100):
        tickers = self.get_all_tickers()
        balances = self.get_account_balances()
        result = {}

        for name, amount in balances.items():
            actual_fills = {}
            current_amount = 0.0
            for currency in self.currencies:
                if name == currency or name == 'BTC':
                    continue
                ticker_id = "{}{}".format(name, currency)
                if ticker_id not in tickers: continue
                orders = self.client.get_my_trades(symbol=ticker_id, limit=limit)
                if not orders or len(orders) == 0: continue

                for order in orders:
                    actual_fills[order['time']] = order

            skip_size = 0.0
            for (k, v) in sorted(actual_fills.items(), reverse=True):
                if v['isBuyer'] == False:
                    skip_size += float(v['qty'])
                    continue

                if float(v['qty']) <= skip_size:
                    skip_size -= float(v['qty'])
                    continue

                if name not in result.keys():
                    result[name] = []

                result[name].append(v)
                current_amount += float(v['qty'])
                if current_amount >= float(amount):
                    break
        return result

    # get all fills by using account balances to backtrack
    def get_all_fills(self, limit=100):
        tickers = self.get_all_tickers()
        balances = self.get_account_balances()
        result = {}

        for name, amount in balances.items():
            actual_fills = {}
            current_amount = 0.0
            for currency in self.currencies:
                if name == currency or name == 'BTC':
                    continue
                ticker_id = "{}{}".format(name, currency)
                if ticker_id not in tickers: continue
                fills = self.client.get_all_orders(symbol=ticker_id, limit=limit)
                if not fills or len(fills) == 0: continue

                for fill in fills:
                    if 'status' not in fill or fill['status'] != 'FILLED': continue
                    actual_fills[fill['time']] = fill

            skip_size = 0.0
            for (k, v) in sorted(actual_fills.items(), reverse=True):
                if v['side'] == 'SELL':
                    skip_size += float(v['executedQty'])
                    continue

                if float(v['executedQty']) <= skip_size:
                    skip_size -= float(v['executedQty'])
                    continue

                if name not in result.keys():
                    result[name] = []

                del v['stopPrice']
                del v['isWorking']
                del v['status']
                del v['timeInForce']
                del v['icebergQty']
                result[name].append(v)
                current_amount += float(v['executedQty'])
                if current_amount >= float(amount):
                    break

        return result

    def get_fills(self, ticker_id=None, limit=100):
        result = []

        if ticker_id is None:
            return self.get_all_fills(limit=limit)

        fills = self.client.get_all_orders(symbol=ticker_id, limit=limit)
        for fill in fills:
            if 'status' not in fill or fill['status'] != 'FILLED': continue
            result.append(fill)
        return result

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(orderId=order_id, symbol=ticker_id)

    def get_orders(self, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id
        return self.client.get_open_orders(symbol=ticker_id)

    def get_account_history(self):
        pass

    def load_buy_price_list(self, base, currency):
        buy_price_list = []
        for trade in self.get_my_trades(base, currency):
            buy_price_list.append(float(trade['price']))
        return sorted(buy_price_list)

    def get_my_trades(self, base, currency, limit=500):
        balances = self.get_account_balances()
        result = []

        symbol = self.make_ticker_id(base, currency)

        amount = 0.0
        if base in balances.keys():
            amount = balances[base]
        actual_fills = {}
        current_amount = 0.0
        orders = self.client.get_my_trades(symbol=symbol, limit=limit)
        for order in orders:
            actual_fills[order['time']] = order

        skip_size = 0.0
        for (k, v) in sorted(actual_fills.items(), reverse=True):
            if v['isBuyer'] == False:
                skip_size += float(v['qty'])
                continue

            if float(v['qty']) <= skip_size:
                skip_size -= float(v['qty'])
                continue

            #if symbol not in result.keys():
            #    result[symbol] = []

            result.append(v)
            current_amount += float(v['qty'])
            if current_amount >= float(amount):
                break
        return result

    def handle_buy_completed(self, price, size):
        pass

    def handle_sell_completed(self, price, size):
        pass

    def get_account_balance(self):
        pass

    def order_market_buy(self, symbol, quantity):
        return self.client.order_market_buy(symbol=symbol, quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.order_market_sell(symbol=symbol, quantity=quantity)

    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = self.round_quote_symbol(ticker_id, float(price) * float(size)) #self.round_quote(price * size)
            if usd_value > cavailable: return False
            #print("buy_market({}, {}, {}".format(size, price, ticker_id))
            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - usd_value, cavailable - usd_value)
            return True
        else:
            self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
            try:
                result = self.order_market_buy(symbol=ticker_id, quantity=size)
            except BinanceAPIException as e:
                self.logger.info(e)
                result = None
            return result


    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bavailable: return False
            #print("sell_market({}, {}, {}".format(size, price, ticker_id))
            usd_value = self.round_quote_symbol(ticker_id, float(price) * float(size))
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable) - float(size))
            self.update_asset_balance(currency, cbalance + usd_value, cavailable + usd_value)
            return True
        else:
            self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
            try:
                result = self.order_market_sell(symbol=ticker_id, quantity=size)
            except BinanceAPIException as e:
                self.logger.info(e)
                result = None
            return result


    # use for both limit orders and stop loss orders
    def buy_limit_complete(self, price, size, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size) #self.round_quote(price * size)
            if usd_value > cbalance: return
            #print("buy_market({}, {}, {}".format(size, price, ticker_id))
            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - usd_value, cavailable)
        else:
            self.get_account_balances()


    # use for both limit orders and stop loss orders
    def sell_limit_complete(self, price, size, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bbalance: return

            usd_value = float(price) * float(size)
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable))
            self.update_asset_balance(currency, cbalance + usd_value, cavailable + usd_value)
        else:
            self.get_account_balances()

    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_buy(timeInForce=timeInForce,
                                               symbol=ticker_id,
                                               quantity=size,
                                               price=price,
                                               stopPrice=stop_price)


    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_sell(timeInForce=timeInForce,
                                               symbol=ticker_id,
                                               quantity=size,
                                               price=price,
                                               stopPrice=stop_price)


    def buy_limit(self, price, size, post_only=True, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_buy(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)


    def sell_limit(self, price, size, post_only=True, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_sell(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)

    def cancel_order(self, orderid, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id
        return self.client.cancel_order(symbol=ticker_id, orderId=orderid)

    def cancel_all(self):
        pass

    def get_klines(self, days=0, hours=1, ticker_id=None):
        if not ticker_id:
            ticker_id = self.ticker_id

        timestr = ''
        if days == 1:
            timestr = "1 day ago"
        elif days > 1:
            timestr = "{} days ago".format(days)
        if days == 0:
            if hours == 1:
                timestr = "1 hour ago"
            elif hours > 1:
                timestr = "{} hours ago".format(hours)
        else:
            if hours == 1:
                timestr = "and 1 hour ago"
            elif hours > 1:
                timestr = "and {} hours ago".format(hours)
        timestr += " UTC"

        klines_data = self.client.get_historical_klines(ticker_id, Client.KLINE_INTERVAL_1MINUTE, timestr)

        # reorganize kline format to same as GDAX for consistency:
        # GDAX kline format: [ timestamp, low, high, open, close, volume ]
        # binance format: [opentime, open, high, low, close, volume, closetime quotevolume, tradecount,
        # taker_buy_base_volume, taker_buy_currency_volume, ignore]
        klines = []
        for k in klines_data:
            ts = k[0] / 1000
            klines.append([ts, k[3], k[2], k[1], k[4], k[5]])

        return klines
