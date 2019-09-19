from trader.account.AccountBase import AccountBase
from trader.lib.struct.Message import Message
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
from trader.account.cbpro import AuthenticatedClient, PublicClient
from trader.config import *
import json
import os
from datetime import datetime, timedelta


class AccountCoinbasePro(AccountBase):
    def __init__(self, client=None, simulation=False, logger=None, simulate_db_filename=None):
        self.exchange_name = 'cbpro'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate = simulation
        self.simulate_db_filename = simulate_db_filename
        if client:
            self.client = client
        elif not self.simulate:
            self.client = AuthenticatedClient(CBPRO_KEY, CBPRO_SECRET, CBPRO_PASS)
        self.pc = PublicClient()
        self.info_all_assets = {}
        self.details_all_assets = {}
        self.balances = {}

        # keep track of initial currency buy size, and subsequent trades against currency
        #self._currency_buy_size = {}
        #for currency in self.currencies:
        #    self._currency_buy_size[currency] = 0

        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self.loaded_model_count = 0

    def format_ts(self, ts):
        return int(ts)

    def ts_to_seconds(self, ts):
        return float(ts / 1000.0)

    # returns true if this ts is an hourly ts
    def is_hourly_ts(self, ts):
        hourly_ts = self.get_hourly_ts(ts)
        return int(ts) == hourly_ts

    # set minutes and seconds components of timestamp to zero
    def get_hourly_ts(self, ts):
        #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
        #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
        return int(self.ts_to_seconds(ts) / 3600.0) * 3600 * 1000

    def seconds_to_ts(self, seconds):
        return float(seconds * 1000)

    def hours_to_ts(self, hours):
        return float(hours * 3600 * 1000)

    def get_ticker(self, symbol):
        if not self.simulate and len(self._tickers) == 0:
            self._tickers = self.get_all_tickers()
        try:
            price = self._tickers[symbol]
        except KeyError:
            price = 0.0
        return price

    def update_ticker(self, symbol, price, ts):
        if self.simulate:
            last_price = 0
            try:
                last_price = self._tickers[symbol]
            except KeyError:
                pass

            if not last_price:
                self._min_tickers[symbol] = [price, ts]
                self._max_tickers[symbol] = [price, ts]
            else:
                if price < self._min_tickers[symbol][0]:
                    self._min_tickers[symbol] = [price, ts]
                elif price > self._max_tickers[symbol][0]:
                    self._max_tickers[symbol] = [price, ts]

        self._tickers[symbol] = price

    def update_tickers(self, tickers):
        for symbol, price in tickers.items():
            self._tickers[symbol] = float(price)

    def get_tickers(self):
        return self._tickers

    def get_min_tickers(self):
        return self._min_tickers

    def get_max_tickers(self):
        return self._max_tickers

    def set_trader_profit_mode(self, mode):
        if mode in self.currencies:
            self._trader_profit_mode = mode
        else:
            self.logger.info("set_trader_profit_mode({}) FAILED".format(mode))

    def get_trader_profit_mode(self):
        return self._trader_profit_mode

    def set_total_percent_profit(self, tpprofit):
        self._tpprofit = tpprofit

    def get_total_percent_profit(self):
        return self._tpprofit

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

    def round_base(self, price, base_increment=0):
        if base_increment:
            try:
                precision = '{:.8f}'.format(float(base_increment)).index('1')
                if float(base_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_base(): index not found in {}, price={}".format(base_increment, price))
                return price

            return round(float(price), precision)
        return price

    def round_quote(self, price, quote_increment=0):
        if quote_increment:
            try:
                precision = '{:.8f}'.format(float(quote_increment)).index('1')
                if float(quote_increment) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quote(): index not found in {}, price={}".format(quote_increment, price))
                return price
            return round(float(price), precision)
        return price

    def round_quantity(self, size, min_qty=0):
        if min_qty:
            try:
                precision = '{:.8f}'.format(float(min_qty)).index('1')
                if float(min_qty) < 1.0:
                    precision -= 1
            except ValueError:
                self.logger.warning("round_quantity(): index not found in {}, size={}".format(min_qty, size))
                return size
            return round(float(size), precision)
        return size

    def round_base_symbol(self, symbol, price):
        base_increment = self.get_asset_info_dict(symbol=symbol, field='base_step_size')
        return self.round_base(price, base_increment)

    def round_quantity_symbol(self, symbol, size):
        min_qty = self.get_asset_info_dict(symbol=symbol, field='min_qty')
        return self.round_quantity(size, min_qty)

    def round_quote_symbol(self, symbol, price):
        quote_increment = self.get_asset_info_dict(symbol=symbol, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def round_quote_pair(self, base, currency, price):
        quote_increment = self.get_asset_info_dict(base=base, currency=currency, field='currency_step_size')
        return self.round_quote(price, quote_increment)

    def my_float(self, value):
        if float(value) >= 0.1:
            return "{}".format(float(value))
        else:
            return "{:.8f}".format(float(value))

    def make_ticker_id(self, base, currency):
        return '%s-%s' % (base, currency)

    def split_ticker_id(self, symbol):
        base_name = None
        currency_name = None

        parts = symbol.split('-')
        if len(parts) == 2:
            base_name = parts[0]
            currency_name = parts[1]

        return base_name, currency_name

    def split_symbol(self, symbol):
        return self.split_ticker_id(symbol)

    def get_symbol_base(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[0]
        return None

    def get_symbol_currency(self, symbol):
        result = self.split_ticker_id(symbol)
        if result:
            return result[1]
        return None

    # For simulation: load exchange info from file, or call get_exchange_info() and save to file
    def load_exchange_info(self):
        if not self.simulate:
            info = self.get_exchange_info()
            self.info_all_assets = info['pairs']
            self.details_all_assets = info['assets']
            return

        print(self.exchange_info_file)
        if not os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            print(info)
            with open(self.exchange_info_file, 'w') as f:
                json.dump(info, f, indent=4)
        else:
            info = json.loads(open(self.exchange_info_file).read())
        self.info_all_assets = info['pairs']
        self.details_all_assets = info['assets']

    # get exchange info from exchange via API
    def get_exchange_info(self):
        pair_info = self.pc.get_products()
        asset_info = {} #self.client.get_asset_details()
        return self.parse_exchange_info(pair_info, asset_info)

    def parse_exchange_info(self, pair_info, asset_info):
        exchange_info = {}
        pairs = {}

        for info in pair_info:
            symbol = info['id']
            min_qty = info['base_min_size']
            min_price = info['min_market_funds']
            base_step_size = info['base_increment']
            currency_step_size = info['quote_increment']
            pairs[symbol] = {'min_qty': min_qty,
                             'min_price': min_price,
                             'base_step_size': base_step_size,
                             'currency_step_size': currency_step_size,
                             #'minNotional': minNotional,
                             #'commissionAsset': commissionAsset,
                             #'baseAssetPrecision': baseAssetPrecision,
                             #'quotePrecision': quotePrecision,
                             #'orderTypes': orderTypes
                            }

        exchange_info['pairs'] = pairs
        exchange_info['assets'] = asset_info

        return exchange_info


    def get_asset_status(self, name=None):
        if not self.details_all_assets:
            self.load_exchange_info()

        result = self.details_all_assets
        if 'assetDetail' in result.keys():
            self.details_all_assets = result['assetDetail']

        if name and name in self.details_all_assets.keys():
            return self.details_all_assets[name]

        return None


    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        if not self.info_all_assets:
            self.load_exchange_info()

        if not symbol:
            symbol = self.make_ticker_id(base, currency)

        if not self.info_all_assets or symbol not in self.info_all_assets.keys():
            self.logger.warning("symbol {} not found in assets".format(symbol))
            return None
        if field:
            if field not in self.info_all_assets[symbol]:
                self.logger.warning("field {} not found in assets for symbol {}".format(field, symbol))
                return None
            return self.info_all_assets[symbol][field]
        return self.info_all_assets[symbol]

    def get_base_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['base_step_size']

    def get_currency_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['currency_step_size']

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['min_qty']
        min_notional=info['minNotional']
        if float(min_qty) < float(min_notional):
            min_qty = min_notional
        min_price=info['min_price']
        base_step_size=info['base_step_size']
        currency_step_size=info['currency_step_size']
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)
        baseAssetPrecision = info['baseAssetPrecision']
        quotePrecision = info['quotePrecision']
        orderTypes = []
        for order_type in info['orderTypes']:
            orderTypes.append(self.get_order_msg_type(order_type))

        result = AssetInfo(base=base,
                           currency=currency,
                           min_qty=min_qty,
                           min_price=min_price,
                           base_step_size=base_step_size,
                           currency_step_size=currency_step_size,
                           is_currency_pair=is_currency_pair,
                           baseAssetPrecision=baseAssetPrecision,
                           quotePrecision=quotePrecision,
                           orderTypes=orderTypes
                           )
        return result


    def get_order_msg_type(self, order_type):
        if order_type == 'MARKET':
            msg_type = Message.TYPE_MARKET
        elif order_type == 'LIMIT':
            msg_type = Message.TYPE_LIMIT
        elif order_type == 'LIMIT_MAKER':
            msg_type = Message.TYPE_LIMIT_MAKER
        elif order_type == "STOP_LOSS":
            msg_type = Message.TYPE_STOP_LOSS
        elif order_type == "STOP_LOSS_LIMIT":
            msg_type = Message.TYPE_STOP_LOSS_LIMIT
        elif order_type == "TAKE_PROFIT_LIMIT":
            msg_type = Message.TYPE_PROFIT_LIMIT
        elif order_type == "TAKE_PROFIT":
            msg_type = Message.TYPE_TAKE_PROFIT
        else:
            msg_type = Message.TYPE_NONE
        return msg_type


    def get_order_msg_cmd(self, order_type, side):
        if order_type == 'MARKET' and side == 'BUY':
            type = Message.MSG_MARKET_BUY
        elif order_type == 'MARKET' and side == 'SELL':
            type = Message.MSG_MARKET_SELL
        elif order_type == 'LIMIT' and side == 'BUY':
            type = Message.MSG_LIMIT_BUY
        elif order_type == 'LIMIT' and side == 'SELL':
            type = Message.MSG_LIMIT_SELL
        elif order_type == "STOP_LOSS" and side == 'BUY':
            type = Message.MSG_STOP_LOSS_BUY
        elif order_type == "STOP_LOSS" and side == 'SELL':
            type = Message.MSG_STOP_LOSS_SELL
        elif order_type == "STOP_LOSS_LIMIT" and side == "BUY":
            type = Message.MSG_STOP_LOSS_LIMIT_BUY
        elif order_type == "STOP_LOSS_LIMIT" and side == "SELL":
            type = Message.MSG_STOP_LOSS_LIMIT_SELL
        elif order_type == "TAKE_PROFIT_LIMIT" and side == "BUY":
            type = Message.MSG_PROFIT_LIMIT_BUY
        elif order_type == "TAKE_PROFIT_LIMIT" and side == "SELL":
            type = Message.MSG_PROFIT_LIMIT_SELL
        elif order_type == "TAKE_PROFIT" and side == "BUY":
            type = Message.MSG_TAKE_PROFIT_BUY
        elif order_type == "TAKE_PROFIT" and side == "SELL":
            type = Message.MSG_TAKE_PROFIT_SELL
        else:
            type = Message.MSG_NONE
        return type

    def parse_order_update(self, result):
        symbol = None
        orig_id = None
        order_id = None
        side = None
        order_type = None
        order_price = 0
        stop_price = 0
        order_size = 0
        order_status = None
        exec_type = None
        reject_reason = None
        ts = 0

        if self.simulate:
            return None

        # maybe use for debug
        #self.logger.info("parse_order_update={}".format(result))

        if 'c' in result: order_id = result['c']
        if 'C' in result: orig_id = result['C']
        if 'r' in result: reject_reason = result['r']
        if 's' in result: symbol = result['s']
        if 'S' in result: side = result['S']
        if 'o' in result: order_type = result['o']
        if 'q' in result: order_size = result['q']
        if 'p' in result: order_price = result['p']
        if 'P' in result: stop_price = result['P']
        if 'X' in result: order_status = result['X']
        if 'x' in result: exec_type = result['x']
        if 'T' in result: ts = result['T']

        if not symbol:
            return None

        msg_status = Message.MSG_NONE

        if not order_type:
            return None

        msg_type = self.get_order_msg_type(order_type)

        if exec_type == 'TRADE' and order_status == 'FILLED':
            if side == 'BUY':
                msg_status = Message.MSG_BUY_COMPLETE
            elif side == 'SELL':
                msg_status = Message.MSG_SELL_COMPLETE
        elif exec_type == 'REJECTED' and order_status == 'REJECTED':
            if side == 'BUY':
                msg_status = Message.MSG_BUY_FAILED
            elif side == 'SELL':
                msg_status = Message.MSG_SELL_FAILED

        order_update = OrderUpdate(symbol, order_price, stop_price, order_size, order_type, exec_type,
                                   side, ts, order_id, orig_id, order_status, reject_reason, msg_type, msg_status)

        return order_update


    # parse json response to binance API order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        orderid = None
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

        # maybe use for debug
        #self.logger.info("parse_order_result={}".format(result))

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

        if not symbol or (status != 'FILLED' and status != 'CANCELED'):
            return None

        if not side or not order_type:
            return None

        price = 0
        if len(prices) != 0:
            if side == 'BUY':
                price = max(prices)
            elif side == 'SELL':
                price = min(prices)

        if status == 'FILLED':
            type = self.get_order_msg_cmd(order_type, side)
        elif status == 'CANCELED' and side == 'BUY':
            type = Message.MSG_BUY_CANCEL
        elif status == 'CANCELED' and side == 'SELL':
            type = Message.MSG_SELL_CANCEL
        elif status == 'REJECTED' and side == 'BUY':
            type = Message.MSG_BUY_FAILED
        elif status == 'REJECTED' and side == 'SELL':
            type = Message.MSG_SELL_FAILED

        order = Order(symbol=symbol,
                      price=price,
                      size=origqty,
                      type=type,
                      orderid=orderid,
                      quote_size=quoteqty,
                      commission=commission,
                      sig_id=sigid)

        # maybe use for debug
        #self.logger.info("order: {}".format(str(order)))
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

    def get_account_total_value(self, total_btc_only=False):
        result = {}
        result['assets'] = {}
        tickers = self.get_all_tickers()

        btc_usd_price = float(tickers['BTCUSDT'])
        bnb_btc_price = float(tickers['BNBBTC'])
        total_balance_usd = 0.0
        total_balance_btc = 0.0

        for accnt in self.client.get_account()['balances']:
            if float(accnt['free']) != 0.0 or float(accnt['locked']) != 0.0:
                if accnt['asset'] != 'BTC' and accnt['asset'] != 'USDT':
                    symbol = "{}BTC".format(accnt['asset'])
                    if symbol not in tickers:
                        continue
                    price = float(tickers[symbol])
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = price * total_amount
                elif accnt['asset'] != 'USDT':
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = total_amount
                else:
                    total_amount = float(accnt['free']) + float(accnt['locked'])
                    price_btc = total_amount / btc_usd_price

                price_usd = price_btc * btc_usd_price
                total_balance_usd += price_usd
                total_balance_btc += price_btc

                if price_usd > 1.0:
                    if not total_btc_only:
                        asset = accnt['asset']
                        result['assets'][asset] = {}
                        result['assets'][asset]['amount'] = total_amount
                        result['assets'][asset]['btc'] = price_btc
                        result['assets'][asset]['usd'] = price_usd
        if not total_btc_only:
            result['total'] = {}
            result['total']['btc'] = total_balance_btc
            if bnb_btc_price:
                result['total']['bnb'] = total_balance_btc / bnb_btc_price
            result['total']['usd'] = total_balance_usd
            return result
        return total_balance_btc

    def get_account_total_btc_value(self):
        return self.get_account_total_value(total_btc_only=True)

    def total_btc_available(self, tickers=None):
        if not tickers:
            tickers = self._tickers
        for symbol, info in self.balances.items():
            if symbol != 'BTC':
                if not info or not info['balance']:
                    continue
                ticker_id = "{}BTC".format(symbol)
                if ticker_id not in tickers:
                    return False
        return True


    def get_total_btc_value(self, tickers=None):
        total_balance_btc = 0.0

        if not tickers:
            tickers = self._tickers

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

    # get USDT value of base by calculating (base_currency) * (currency_usdt)
    def get_usdt_value_symbol(self, symbol, price=0):
        currency = self.split_ticker_id(symbol)[1]
        if currency == 'USDT':
            currency_price = 1.0
        else:
            usdt_symbol = self.make_ticker_id(currency, 'USDT')
            currency_price = float(self.get_ticker(usdt_symbol))

        if not currency_price:
            return 0

        if not price:
            price = float(self.get_ticker(symbol))

        if not price:
            return 0

        return currency_price * price

    def update_asset_balance(self, name, balance, available):
        if self.simulate:
            if name in self.balances.keys() and balance == 0.0 and available == 0.0:
                del self.balances[name]
                return
            if name not in self.balances.keys():
                self.balances[name] = {}
            self.balances[name]['balance'] = balance
            self.balances[name]['available'] = available

    # implemented for CoinBase Pro
    def get_account_balances(self):
        self.balances = {}
        result = {}
        for account in self.client.get_accounts():
            asset_name = account['currency']
            balance = account['balance']
            available = account['available']
            hold = account['hold']
            self.balances[asset_name] = {'balance': balance, 'available': available, 'hold': hold}
            result[asset_name] = balance
        return result

    def get_asset_balance(self, asset):
        try:
            result = self.balances[asset]
        except KeyError:
            result = {'balance': 0.0, 'available': 0.0}
        return result

    def get_asset_balance_tuple(self, asset):
        result = self.get_asset_balance(asset)
        try:
            balance = float(result['balance'])
            available = float(result['available'])
        except KeyError:
            balance = 0.0
            available = 0.0
        if 'balance' not in result or 'available' not in result:
            return 0.0, 0.0
        return balance, available

    def get_deposit_history(self, asset=None):
        return self.client.get_deposit_history(asset=asset)

    def get_all_ticker_symbols(self, currency=None):
        result = []
        products = self.pc.get_products()
        for product in products:
            if currency and product['id'].endswith(currency):
                result.append(product['id'])
            else:
                result.append(product['id'])
        return result

    def get_all_tickers(self):
        result = {}
        if not self.simulate:
            for ticker in self.client.get_all_tickers():
                result[ticker['symbol']] = ticker['price']
        else:
            result = self._tickers
        return result

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(orderId=order_id, symbol=ticker_id)

    def get_orders(self, ticker_id=None):
        return self.client.get_open_orders(symbol=ticker_id)

    def order_market_buy(self, symbol, quantity):
        return self.client.place_market_order(product_id=symbol, side='buy', funds=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.place_market_order(product_id=symbol, side='sell', funds=quantity)

    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            size = self.round_base_symbol(ticker_id, size)
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
            if amount > cavailable:
                return False

            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - amount, cavailable - amount)
            return True
        else:
            self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
            #try:
            result = self.order_market_buy(symbol=ticker_id, quantity=size)
            #except BinanceAPIException as e:
            #    self.logger.info(e)
            #    result = None
            return result


    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bavailable:
                self.logger.warning("{}: {} > {}".format(ticker_id, float(size), bavailable))
                return False

            amount = self.round_quote_symbol(ticker_id, float(price) * float(size))
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable) - float(size))
            self.update_asset_balance(currency, cbalance + amount, cavailable + amount)
            return True
        else:
            self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
            #try:
            result = self.order_market_sell(symbol=ticker_id, quantity=size)
            #except BinanceAPIException as e:
            #    self.logger.info(e)
            #    result = None
            return result


    # use for both limit orders and stop loss orders
    def buy_limit_complete(self, price, size, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size) #self.round_quote(price * size)
            if usd_value > cbalance: return False
            #print("buy_market({}, {}, {}".format(size, price, ticker_id))
            self.update_asset_balance(base, bbalance + float(size), bavailable + float(size))
            self.update_asset_balance(currency, cbalance - usd_value, cavailable)
            return True
        else:
            self.get_account_balances()


    # use for both limit orders and stop loss orders
    def sell_limit_complete(self, price, size, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)

            if float(size) > bbalance: return False

            usd_value = float(price) * float(size)
            self.update_asset_balance(base, float(bbalance) - float(size), float(bavailable))
            self.update_asset_balance(currency, cbalance + usd_value, cavailable + usd_value)
            return True
        else:
            self.get_account_balances()


    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return False

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
            return True
        else:
            self.logger.info("buy_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.place_stop_order(product_id=ticker_id, side='buy', price=price, size=size)


    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):

        if self.simulate:
            #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return False

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
            return True
        else:
            self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.place_stop_order(product_id=ticker_id, side='sell', price=price, size=size)


    def buy_limit(self, price, size, post_only=True, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
        else:
            return self.client.place_limit_order(product_id=ticker_id, side='buy', price=price, size=size)


    def sell_limit(self, price, size, post_only=True, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
        else:
            return self.client.place_limit_order(product_id=ticker_id, side='sell', price=price, size=size)

    # for handling a canceled sell order during simulation
    def cancel_sell_limit_complete(self, size, ticker_id=None):
        if not self.simulate:
            return
        base, currency = self.split_ticker_id(ticker_id)
        bbalance, bavailable = self.get_asset_balance_tuple(base)
        self.update_asset_balance(base, float(bbalance), float(bavailable) + float(size))

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_order(symbol=ticker_id, orderId=orderid)

    def cancel_all(self, ticker_id=None):
        return self.client.cancel_all(product_id=ticker_id)

    # The granularity field must be one of the following values: {60, 300, 900, 3600, 21600, 86400}
    # The maximum amount of data returned is 300 candles
    # kline format: [ timestamp, low, high, open, close, volume ]
    def get_klines(self, days=0, hours=1, ticker_id=None):
        end = datetime.utcnow()
        start = (end - timedelta(days=days, hours=hours))
        granularity = 900
        if days == 0 and hours < 6:
            granularity = 60
        elif (days== 0 and hours <= 24) or (days == 1 and hours == 0):
            granularity = 300

        rates = self.pc.get_product_historic_rates(ticker_id,
                                                   start.isoformat(),
                                                   end.isoformat(),
                                                   granularity=granularity)
        return rates[::-1]


    def get_hourly_klines(self, symbol, start_ts, end_ts):
        klines = self.pc.get_product_historic_rates(product_id=symbol,
                                                    start=start_ts,
                                                    end=end_ts,
                                                    granularity=3600)

        return klines
