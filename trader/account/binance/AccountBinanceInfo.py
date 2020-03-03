import os
import json
from trader.account.AccountBaseInfo import AccountBaseInfo
from trader.lib.struct.Order import Order
from trader.lib.struct.AssetInfo import AssetInfo

class AccountBinanceInfo(AccountBaseInfo):
    def __init__(self, client, simulation=False, logger=None, exchange_info_file=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger
        self.exchange_info_file = exchange_info_file
        self.info_all_assets = {}
        self.details_all_assets = {}
        self._exchange_pairs = None
        self.currencies = ['BTC', 'ETH', 'BNB', 'USDT']
        self.currency_trade_pairs = ['ETHBTC', 'BNBBTC', 'BNBETH', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT']
        self.trade_fee = 0.1 / 100.0

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

    def get_trade_fee(self):
        return self.trade_fee

    def get_currencies(self):
        return self.currencies

    def get_currency_trade_pairs(self):
        return self.currency_trade_pairs

    def get_info_all_assets(self):
        return self.info_all_assets

    def get_details_all_assets(self):
        return self.details_all_assets

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

    # determine if asset is available (not disabled or delisted)
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

    def get_asset_status(self, name=None):
        result = None
        if not self.details_all_assets:
            self.load_exchange_info()
        try:
            result = self.details_all_assets[name]
        except KeyError:
            pass
        return result

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
