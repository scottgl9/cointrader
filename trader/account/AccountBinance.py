from trader.account.binance.client import Client, BinanceAPIException
from trader.account.AccountBase import AccountBase
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
import json
import os


#logger = logging.getLogger(__name__)

class AccountBinance(AccountBase):
    def __init__(self, client, simulation=False, logger=None, simulate_db_filename=None):
        self.exchange_type = AccountBase.EXCHANGE_BINANCE
        self.exchange_name = 'binance'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        self.client = client
        self.simulate = simulation
        self.info_all_assets = {}
        self.details_all_assets = {}
        self.balances = {}
        self._trader_mode = AccountBase.TRADER_MODE_NONE

        # hourly db column names
        self.hourly_cnames = ['ts', 'open', 'high', 'low', 'close', 'volume']
        #self.hourly_cnames = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume',
        #                      'trade_count', 'taker_buy_base_volume', 'taker_buy_quote_volume']
        # hourly db column names short list
        #self.hourly_scnames = ['ts', 'open', 'high', 'low', 'close', 'base_volume', 'quote_volume']

        if self.simulate:
            self.currencies = ['BTC', 'ETH', 'BNB', 'USDT']
            self.currency_trade_pairs = ['ETHBTC', 'BNBBTC', 'BNBETH', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT']
        else:
            self.currencies = ['BTC', 'ETH', 'BNB', 'PAX', 'USDT']
            self.currency_trade_pairs = ['ETHBTC', 'BNBBTC', 'BNBETH', 'BTCPAX', 'ETHPAX', 'BNBPAX',
                                         'ETHUSDT', 'BTCUSDT', 'BNBUSDT']

        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.currencies:
            self._currency_buy_size[currency] = 0

        self.client = client

        self._exchange_pairs = None
        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
        self._sell_only = False
        self._btc_only = False
        self._eth_only = False
        self._bnb_only = False
        self._hourly_symbols_only = False
        self._trades_disabled = False
        self._test_stop_loss = False
        self._max_market_buy = 0
        self.loaded_model_count = 0

    # get config section name from trader.ini
    def get_config_section_name(self):
        if self.simulate:
            name = "{}.simulate".format(self.exchange_name)
        else:
            name = "{}.live".format(self.exchange_name)
        return name

    def get_trader_mode(self):
        return self._trader_mode

    def set_trader_mode(self, trader_mode):
        self._trader_mode = trader_mode

    def trade_mode_hourly(self):
        return self._trader_mode == AccountBase.TRADER_MODE_HOURLY

    def trade_mode_realtime(self):
        return self._trader_mode == AccountBase.TRADER_MODE_REALTIME

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

    # if hourly table name doesn't match symbol name
    # ex. symbol 'BTC-USD', table name 'BTC_USD'
    def get_hourly_table_name(self, symbol):
        return symbol

    # get symbol name from hourly table name
    # ex. table name 'BTC_USD', return symbol 'BTC-USD'
    def get_symbol_hourly_table(self, table_name):
        return table_name

    # get hourly db column names
    def get_hourly_column_names(self):
        return self.hourly_cnames

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

    def set_sell_only(self, sell_only):
        self.logger.info("set_sell_only({})".format(sell_only))
        self._sell_only = sell_only

    def sell_only(self):
        return self._sell_only

    def set_btc_only(self, btc_only):
        self.logger.info("set_btc_only({})".format(btc_only))
        self._btc_only = btc_only

    def btc_only(self):
        return self._btc_only

    def set_eth_only(self, eth_only):
        self.logger.info("set_eth_only({})".format(eth_only))
        self._eth_only = eth_only

    def eth_only(self):
        return self._eth_only

    def set_bnb_only(self, bnb_only):
        self.logger.info("set_bnb_only({})".format(bnb_only))
        self._bnb_only = bnb_only

    def bnb_only(self):
        return self._bnb_only

    def set_hourly_symbols_only(self, hourly_symbols_only):
        self.logger.info("set_hourly_symbols_only({})".format(hourly_symbols_only))
        self._hourly_symbols_only = hourly_symbols_only

    def hourly_symbols_only(self):
        return self._hourly_symbols_only

    def set_trades_disabled(self, trades_disabled):
        self.logger.info("set_trades_disabled({})".format(trades_disabled))
        self._trades_disabled = trades_disabled

    def trades_disabled(self):
        return self._trades_disabled

    def set_max_market_buy(self, max_market_buy):
        self.logger.info("set_max_market_buy({})".format(max_market_buy))
        self._max_market_buy = max_market_buy

    def max_market_buy(self):
        return self._max_market_buy

    def set_test_stop_loss(self, test_stop_loss):
        self.logger.info("set_test_stop_loss({})".format(test_stop_loss))
        self._test_stop_loss = test_stop_loss

    def test_stop_loss(self):
        return self._test_stop_loss

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
        if not self.simulate and os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            self.info_all_assets = info['pairs']
            self.details_all_assets = info['assets']
            return

        if not os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            with open(self.exchange_info_file, 'w') as f:
                json.dump(info, f, indent=4)
        else:
            info = json.loads(open(self.exchange_info_file).read())
        self.info_all_assets = info['pairs']
        self.details_all_assets = info['assets']

    # get exchange info from exchange via API
    def get_exchange_info(self):
        pair_info = self.client.get_exchange_info()
        asset_info = self.client.get_asset_details()
        return self.parse_exchange_info(pair_info, asset_info)

    def parse_exchange_info(self, pair_info, asset_info):
        exchange_info = {}
        pairs = {}
        assets = {}
        #if not info:
        #    info = self.client.get_exchange_info()

        # process pairs
        for key, value in pair_info.items():
            if key != 'symbols':
                continue
            for pair in value:
                minNotional = ''
                min_qty = ''
                min_price = ''
                currency_step_size = ''
                base_step_size = ''
                commissionAsset = ''
                baseAssetPrecision = 8
                quotePrecision = 8
                orderTypes = ''

                if 'baseAssetPrecision' in pair:
                    baseAssetPrecision = pair['baseAssetPrecision']
                if 'quotePrecision' in pair:
                    quotePrecision = pair['quotePrecision']

                for filter in pair['filters']:
                    # skip MARKET_LOT_SIZE
                    if filter['filterType'] == 'MARKET_LOT_SIZE':
                        continue

                    if 'minQty' in filter:
                        min_qty = filter['minQty']
                    if 'minPrice' in filter:
                        min_price = filter['minPrice']
                    if 'tickSize' in filter:
                        currency_step_size = filter['tickSize']
                    if 'stepSize' in filter:
                        base_step_size = filter['stepSize']
                    if 'minNotional' in filter:
                        minNotional = filter['minNotional']
                    if 'commissionAsset' in filter:
                        commissionAsset = filter['commissionAsset']

                if 'orderTypes' in pair:
                    orderTypes = ','.join(pair['orderTypes'])

                pairs[pair['symbol']] = {'min_qty': min_qty,
                                           'min_price': min_price,
                                           'currency_step_size': currency_step_size,
                                           'base_step_size': base_step_size,
                                           'minNotional': minNotional,
                                           'commissionAsset': commissionAsset,
                                           'baseAssetPrecision': baseAssetPrecision,
                                           'quotePrecision': quotePrecision,
                                           'orderTypes': orderTypes
                                           }

        # process assets
        for key, value in asset_info['assetDetail'].items():
            assets[key] = {}
            if not value['depositStatus'] or not value['withdrawStatus']:
                assets[key]['disabled'] = True
            else:
                assets[key]['disabled'] = False
            if assets[key]['disabled'] and 'depositTip' in value:
                assets[key]['delisted'] = True
            else:
                assets[key]['delisted'] = False

        exchange_info['pairs'] = pairs
        exchange_info['assets'] = assets

        return exchange_info

    # get list of exchange pairs (trade symbols)
    def get_exchange_pairs(self):
        if not self._exchange_pairs:
            self.load_exchange_info()
        return self._exchange_pairs

    # is a valid exchange pair
    def is_exchange_pair(self, symbol):
        if not self._exchange_pairs:
            self.load_exchange_info()
        if symbol in self._exchange_pairs:
            return True
        return False

    def get_asset_status(self, name=None):
        result = None
        if not self.details_all_assets:
            self.load_exchange_info()
        try:
            result = self.details_all_assets[name]
        except KeyError:
            pass
        return result

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
            orderTypes.append(Order.get_order_msg_type(order_type))

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

        msg_status = TraderMessage.MSG_NONE

        if not order_type:
            return None

        msg_type = Order.get_order_msg_type(order_type)

        if exec_type == 'TRADE' and order_status == 'FILLED':
            if side == 'BUY':
                msg_status = TraderMessage.MSG_BUY_COMPLETE
            elif side == 'SELL':
                msg_status = TraderMessage.MSG_SELL_COMPLETE
        elif exec_type == 'REJECTED' and order_status == 'REJECTED':
            if side == 'BUY':
                msg_status = TraderMessage.MSG_BUY_FAILED
            elif side == 'SELL':
                msg_status = TraderMessage.MSG_SELL_FAILED

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

        side_type = Order.SIDE_UNKNOWN
        if side == 'BUY':
            side_type = Order.SIDE_BUY
        elif side == 'SELL':
            side_type = Order.SIDE_SELL

        if status == 'FILLED':
            type = TraderMessage.get_order_msg_cmd(order_type, side)
        elif status == 'CANCELED' and side == 'BUY':
            type = TraderMessage.MSG_BUY_CANCEL
        elif status == 'CANCELED' and side == 'SELL':
            type = TraderMessage.MSG_SELL_CANCEL
        elif status == 'REJECTED' and side == 'BUY':
            type = TraderMessage.MSG_BUY_FAILED
        elif status == 'REJECTED' and side == 'SELL':
            type = TraderMessage.MSG_SELL_FAILED

        order = Order(symbol=symbol,
                      price=price,
                      size=origqty,
                      type=type,
                      side=side_type,
                      orderid=orderid,
                      quote_size=quoteqty,
                      commission=commission,
                      sig_id=sigid)

        # maybe use for debug
        #self.logger.info("order: {}".format(str(order)))
        return order

    # determine if asset is available (not disabled or delisted)
    # if not, don't trade
    def is_asset_available(self, name):
        if name not in self.details_all_assets.keys():
            return False
        status = self.get_asset_status(name)
        try:
            if status['disabled']:
                return False
            if status['delisted']:
                return False
        except KeyError:
            return False
        return True

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

    def total_bnb_available(self, tickers=None):
        if not tickers:
            tickers = self._tickers

        if 'BNBBTC' not in tickers:
            return False
        for symbol, info in self.balances.items():
            if symbol != 'BNB':
                if not info or not info['balance']:
                    continue
                ticker_id = "{}BNB".format(symbol)
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

    def get_total_bnb_value(self, tickers=None):
        if not tickers:
            tickers = self._tickers
        try:
            bnb_btc_value = tickers['BNBBTC']
        except KeyError:
            return 0
        total_balance_btc = self.get_total_btc_value(tickers)
        return total_balance_btc / bnb_btc_value

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

    def get_account_balances(self, detailed=False):
        self.balances = {}
        result = {}
        for funds in self.client.get_account()['balances']:
            funds_free = float(funds['free'])
            funds_locked = float(funds['locked'])
            if funds_free == 0.0 and funds_locked == 0.0: continue
            asset_name = funds['asset']
            self.balances[asset_name] = {'balance': (funds_free + funds_locked), 'available': funds_free}
            result[asset_name] = funds_free + funds_locked
        if detailed:
            return self.balances
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
        if not self.simulate:
            for ticker in self.client.get_all_tickers():
                if currency and ticker['symbol'].endswith(currency):
                    result.append(ticker['symbol'])
                elif not currency:
                    result.append(ticker['symbol'])
        else:
            result = self.info_all_assets.keys()
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

    def get_account_history(self):
        pass

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


    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.buy_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
            try:
                result = self.client.order_market_buy(symbol=ticker_id, quantity=size)
            except BinanceAPIException as e:
                self.logger.info(e)
                result = None
            return result


    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.sell_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
            try:
                result = self.client.order_market_sell(symbol=ticker_id, quantity=size)
            except BinanceAPIException as e:
                self.logger.info(e)
                result = None
            return result


    def buy_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.buy_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            self.logger.info("buy_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     timeInForce=Client.TIME_IN_FORCE_GTC,
                                     side=Client.SIDE_BUY,
                                     type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                                     quantity=size,
                                     price=price,
                                     stopPrice=stop_price)


    def sell_limit_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            return self.sell_limit_stop_simulate(price, size, stop_price, ticker_id)
        else:
            self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     timeInForce=Client.TIME_IN_FORCE_GTC,
                                     side=Client.SIDE_SELL,
                                     type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                                     quantity=size,
                                     price=price,
                                     stopPrice=stop_price)


    def buy_limit_profit(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return False

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
            return True
        else:
            self.logger.info("buy_limit_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     timeInForce=Client.TIME_IN_FORCE_GTC,
                                     side=Client.SIDE_BUY,
                                     type=Client.ORDER_TYPE_TAKE_PROFIT_LIMIT,
                                     quantity=size,
                                     price=price,
                                     stopPrice=stop_price)


    def sell_limit_profit(self, price, size, stop_price, ticker_id=None):

        if self.simulate:
            #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return False

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
            return True
        else:
            self.logger.info("sell_limit_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     timeInForce=Client.TIME_IN_FORCE_GTC,
                                     side=Client.SIDE_SELL,
                                     type=Client.ORDER_TYPE_TAKE_PROFIT_LIMIT,
                                     quantity=size,
                                     price=price,
                                     stopPrice=stop_price)


    def buy_market_profit(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return False

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
            return True
        else:
            self.logger.info("buy_market_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     side=Client.SIDE_BUY,
                                     type=Client.ORDER_TYPE_TAKE_PROFIT,
                                     quantity=size,
                                     stopPrice=stop_price)


    def sell_market_profit(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return False

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
            return True
        else:
            self.logger.info("sell_market_profit({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     side=Client.SIDE_SELL,
                                     type=Client.ORDER_TYPE_TAKE_PROFIT,
                                     quantity=size,
                                     stopPrice=stop_price)


    def buy_market_stop(self, price, size, stop_price, ticker_id=None):
        if self.simulate:
            base, currency = self.split_ticker_id(ticker_id)
            cbalance, cavailable = self.get_asset_balance_tuple(currency)
            usd_value = float(price) * float(size)  # self.round_quote(price * size)

            if usd_value > cavailable: return False

            self.update_asset_balance(currency, cbalance, cavailable - usd_value)
            return True
        else:
            self.logger.info("buy_market_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     side=Client.SIDE_BUY,
                                     type=Client.ORDER_TYPE_STOP_LOSS,
                                     quantity=size,
                                     stopPrice=stop_price)


    def sell_market_stop(self, price, size, stop_price, ticker_id=None):

        if self.simulate:
            #self.logger.info("sell_limit_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            base, currency = self.split_ticker_id(ticker_id)
            bbalance, bavailable = self.get_asset_balance_tuple(base)

            if float(size) > bavailable: return False

            self.update_asset_balance(base, float(bbalance), float(bavailable) - float(size))
            return True
        else:
            self.logger.info("sell_market_stop({}, {}, {}, {}".format(price, size, stop_price, ticker_id))
            return self.client.create_order(symbol=ticker_id,
                                     side=Client.SIDE_SELL,
                                     type=Client.ORDER_TYPE_STOP_LOSS,
                                     quantity=size,
                                     stopPrice=stop_price)


    def buy_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.buy_limit_simulate(price, size, ticker_id)
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_buy(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)


    def sell_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.sell_limit_simulate(price, size, ticker_id)
        else:
            timeInForce = Client.TIME_IN_FORCE_GTC
            return self.client.order_limit_sell(timeInForce=timeInForce, symbol=ticker_id, quantity=size, price=price)


    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel_order(symbol=ticker_id, orderId=orderid)

    def cancel_all(self):
        pass

    def get_klines(self, days=0, hours=1, ticker_id=None):
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

    def get_hourly_klines(self, symbol, start_ts, end_ts):
        result = []
        klines = self.client.get_historical_klines_generator(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            start_str=start_ts,
            end_str=end_ts,
        )
        # ['ts', 'open', 'high', 'low', 'close', 'quote_volume']
        for k in klines:
            result.append([k[0], k[1], k[2], k[3], k[4], k[6]])

        return result
