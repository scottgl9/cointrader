from trader.account.bittrex.bittrex import Bittrex, API_V2_0
from trader.account.AccountBase import AccountBase
from trader.lib.struct.TraderMessage import TraderMessage
from trader.lib.struct.Order import Order
from trader.lib.struct.OrderUpdate import OrderUpdate
from trader.lib.struct.AssetInfo import AssetInfo
from trader.config import *

import json
import os


#logger = logging.getLogger(__name__)

class AccountBittrex(AccountBase):
    def __init__(self, client=None, simulation=False, logger=None, simulate_db_filename=None):
        super(AccountBittrex, self).__init__(client, simulation, logger, simulate_db_filename)
        self.exchange_type = AccountBase.EXCHANGE_BITTREX
        self.exchange_name = 'bittrex'
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.logger = logger
        self.simulate_db_filename = simulate_db_filename
        if client:
            self.client = client
        else:
            self.client = Bittrex(api_key=BITTREX_API_KEY, api_secret=BITTREX_API_SECRET, api_version=API_V2_0)
        self.simulate = simulation
        self.info_all_assets = {}
        self.details_all_assets = {}
        self.balances = {}
        self._trader_mode = AccountBase.TRADER_MODE_NONE

        self.currencies = ['BTC', 'ETH', 'USDT', 'USD']
        self.currency_trade_pairs = ['BTC-ETH', 'USD-BTC', 'USD-ETH', 'USD-USDT', 'USDT-BTC', 'USDT-ETH']
   
        # keep track of initial currency buy size, and subsequent trades against currency
        self._currency_buy_size = {}
        for currency in self.currencies:
            self._currency_buy_size[currency] = 0

        self.client = client

        self._tickers = {}
        self._min_tickers = {}
        self._max_tickers = {}
        self._trader_profit_mode = 'BTC'
        self._tpprofit = 0
        self.initial_currency = 0
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
        base_increment = self.get_asset_info_dict(symbol=symbol, field='stepSize')
        return self.round_base(price, base_increment)

    def round_quantity_symbol(self, symbol, size):
        min_qty = self.get_asset_info_dict(symbol=symbol, field='minQty')
        return self.round_quantity(size, min_qty)

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
            return "{:.8f}".format(float(value))

    def make_ticker_id(self, base, currency):
        return '%s-%s' % (currency, base)

    def split_ticker_id(self, symbol):
        base_name = None
        currency_name = None

        parts = symbol.split('-')
        if len(parts) == 2:
            currency_name = parts[0]
            base_name = parts[1]

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
                baseAssetPrecision = 8
                quotePrecision = 8
                orderTypes = ''

                if 'baseAssetPrecision' in asset:
                    baseAssetPrecision = asset['baseAssetPrecision']
                if 'quotePrecision' in asset:
                    quotePrecision = asset['quotePrecision']

                for filter in asset['filters']:
                    # skip MARKET_LOT_SIZE
                    if filter['filterType'] == 'MARKET_LOT_SIZE':
                        continue

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

                if 'orderTypes' in asset:
                    orderTypes = ','.join(asset['orderTypes'])

                assets[asset['symbol']] = {'minQty': minQty,
                                           'minPrice': minPrice,
                                           'tickSize': tickSize,
                                           'stepSize': stepSize,
                                           'minNotional': minNotional,
                                           'commissionAsset': commissionAsset,
                                           'baseAssetPrecision': baseAssetPrecision,
                                           'quotePrecision': quotePrecision,
                                           'orderTypes': orderTypes
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
            self.load_info_all_assets()

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
        return info['stepSize']

    def get_currency_step_size(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return 0
        return info['tickSize']

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['minQty']
        min_notional=info['minNotional']
        if float(min_qty) < float(min_notional):
            min_qty = min_notional
        min_price=info['minPrice']
        base_step_size=info['stepSize']
        currency_step_size=info['tickSize']
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
        # order_update = OrderUpdate(symbol, order_price, stop_price, order_size, order_type, exec_type,
        #                            side, ts, order_id, orig_id, order_status, reject_reason, msg_type, msg_status)
        #
        # return order_update
        pass


    # parse json response to API order, then use to create Order object
    def parse_order_result(self, result, symbol=None, sigid=0):
        # order = Order(symbol=symbol,
        #               price=price,
        #               size=origqty,
        #               type=type,
        #               orderid=orderid,
        #               quote_size=quoteqty,
        #               commission=commission,
        #               sig_id=sigid)
        #
        # return order
        pass


    # determine if asset is available (not disabled or delisted)
    # if not, don't trade
    def is_asset_available(self, name):
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

    def get_account_balances(self):
        self.balances = {}
        result = {}

        info_balances = self.client.get_balances()
        if not info_balances['success']:
            return self.balances
        for info in info_balances['result']:
            cinfo = info['Currency']
            if not cinfo['IsActive'] or cinfo['IsDeleted'] or cinfo['IsRestricted']:
                continue
            if 'Balance' not in info:
                continue
            binfo = info['Balance']
            print(binfo)
            asset_name = binfo['Currency']
            balance = binfo['Balance']
            available = binfo['Available']
            pending = binfo['Pending']
            self.balances[asset_name] = {'balance': balance,
                                         'available': available }
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
            info_tickers = self.client.get_market_summaries()
            if not info_tickers['success']:
                return result
            for info in info_tickers['result']:
                #market_info = info['Market']
                market_summary = info['Summary']
                ticker_id = market_summary['MarketName']
                price = market_summary['Last']
                result[ticker_id] = price
        else:
            result = self._tickers
        return result

    def get_order(self, order_id, ticker_id):
        return self.client.get_order(orderId=order_id, symbol=ticker_id)

    def get_orders(self, ticker_id=None):
        return self.client.get_open_orders(symbol=ticker_id)

    def order_market_buy(self, symbol, quantity):
        return self.client.trade_buy(market=symbol, order_type='MARKET', quantity=quantity)

    def order_market_sell(self, symbol, quantity):
        return self.client.trade_sell(market=symbol, order_type='MARKET', quantity=quantity)

    def buy_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.buy_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("buy_market({}, {}, {})".format(size, price, ticker_id))
            result = self.client.trade_buy(market=ticker_id, order_type='MARKET', quantity=size)
            return result

    def sell_market(self, size, price=0.0, ticker_id=None):
        if self.simulate:
            return self.sell_market_simulate(size, price, ticker_id)
        else:
            self.logger.info("sell_market({}, {}, {})".format(size, price, ticker_id))
            result = self.client.trade_sell(market=ticker_id, order_type='MARKET', quantity=size)
            return result

    def buy_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.buy_limit_simulate(price, size, ticker_id)
        else:
            result = self.client.trade_buy(market=ticker_id,
                                           order_type='LIMIT',
                                           quantity=size,
                                           time_in_effect='GOOD_TIL_CANCELLED',
                                           condition_type='LESS_THAN',
                                           target=price)
            return result


    def sell_limit(self, price, size, ticker_id=None):
        if self.simulate:
            return self.sell_limit_simulate(price, size, ticker_id)
        else:
            result = self.client.trade_sell(market=ticker_id,
                                           order_type='LIMIT',
                                           quantity=size,
                                           time_in_effect='GOOD_TIL_CANCELLED',
                                           condition_type='GREATER_THAN',
                                           target=price)
            return result

    def cancel_order(self, orderid, ticker_id=None):
        return self.client.cancel(uuid=orderid)

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
        klines = self.client.get_historical_klines_generator(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            start_str=start_ts,
            end_str=end_ts,
        )

        return klines