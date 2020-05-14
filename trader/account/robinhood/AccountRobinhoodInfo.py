import os
import json
from trader.account.AccountBaseInfo import AccountBaseInfo
from trader.lib.struct.Order import Order
from trader.lib.struct.AssetInfo import AssetInfo
from trader.lib.struct.Exchange import Exchange

class AccountRobinhoodInfo(AccountBaseInfo):
    def __init__(self, client, simulate=False, logger=None):
        self.client = client
        self.simulate = simulate
        self.logger = logger
        self.exchange_type = Exchange.EXCHANGE_ROBINHOOD
        self.exchange_name = Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.info_all_assets = {}
        self.details_all_assets = {}
        self._exchange_pairs = None
        self.currencies = ['USD']
        self.currency_trade_pairs = []
        self.trade_fee = 0.0
        self._trader_mode = Exchange.TRADER_MODE_NONE
        self._account_mode = Exchange.ACCOUNT_MODE_CRYPTO

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

    def get_trader_mode(self):
        return self._trader_mode

    def set_trader_mode(self, trader_mode):
        self._trader_mode = trader_mode

    def get_account_mode(self):
        return self._account_mode

    def set_account_mode(self, account_mode):
        self._account_mode = account_mode

    def get_ticker_id(self, symbol):
        try:
            info = self.get_info_all_assets()[symbol]
            return info['id']
        except KeyError:
            return ''

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

    # get list of watched stock urls
    def get_watched_stock_urls(self, all_watched=False):
        watchlists = []
        result = []
        if all_watched:
            for r in self.client.get_all_watchlists():
                watchlists.append(r['name'])
        else:
            watchlists.append('Default')
        for wl in watchlists:
            r = self.client.get_watchlist_by_name(name=wl)
            for e in r:
                result.append(e['instrument'])
        return result

    # get list of watched stock ids
    def get_watched_stock_ids(self, all_watched=False, urls=None):
        result = []
        if not urls:
            urls = self.get_watched_stock_urls(all_watched)
        for url in urls:
            result.append(url.split('/')[-2])
        return result

    # get list of watched stock symbols
    def get_watched_stock_symbols(self, all_watched=False, urls=None):
        result = []
        if not urls:
            urls = self.get_watched_stock_urls(all_watched)
        for e in urls:
            result.append(self.client.get_symbol_by_url(e))
        return result

    # For simulation: load exchange info from file, or call get_exchange_info() and save to file
    def load_exchange_info(self):
        if not self.simulate and os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            self.info_all_assets = info['pairs']
            self.details_all_assets = info['assets']
            return

        print(self.exchange_info_file)
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
        pair_info = self.client.get_crypto_currency_pairs()
        asset_info = None
        return self.parse_exchange_info(pair_info, asset_info)

    def parse_exchange_info(self, pair_info, asset_info):
        exchange_info = {}
        pairs = {}
        assets = {}
        self._exchange_pairs = []

        for info in pair_info:
            tradability = info['tradability']
            if tradability != 'tradable':
                continue
            symbol = info['symbol']
            asset_currency = info['asset_currency']
            quote_currency = info['quote_currency']
            # base info
            #asset_id = asset_currency['id']
            min_qty = info['min_order_size']
            base_step_size = asset_currency['increment']
            #currency_step_size = asset_currency['min_order_price_increment']
            # quote info
            #quote_id = quote_currency['id']
            currency_step_size = quote_currency['increment']
            self._exchange_pairs.append(symbol)
            pairs[symbol] = {'id': info['id'],
                             'min_qty': min_qty,
                             'base_step_size': base_step_size,
                             'currency_step_size': currency_step_size
                            }

        exchange_info['pairs'] = pairs
        exchange_info['assets'] = assets

        return exchange_info

    # get list of exchange pairs (trade symbols)
    def get_exchange_pairs(self):
        if not self._exchange_pairs:
            self.load_exchange_info()

        return sorted(self._exchange_pairs)

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

    # return asset info in AssetInfo class object
    def get_asset_info(self, symbol=None, base=None, currency=None):
        info = self.get_asset_info_dict(symbol=symbol, base=base, currency=currency)
        if not info:
            return None

        min_qty=info['min_qty']

        try:
            min_notional=info['minNotional']
        except KeyError:
            min_notional = min_qty

        if float(min_qty) < float(min_notional):
            min_qty = min_notional
        min_price=info['min_price']
        base_step_size=info['base_step_size']
        currency_step_size=info['currency_step_size']
        is_currency_pair = self.is_currency_pair(symbol=symbol, base=base, currency=currency)

        try:
            baseAssetPrecision = info['baseAssetPrecision']
            quotePrecision = info['quotePrecision']
        except KeyError:
            baseAssetPrecision = 8
            quotePrecision = 8

        orderTypes = []

        try:
            for order_type in info['orderTypes']:
                orderTypes.append(Order.get_order_msg_type(order_type))
        except KeyError:
            pass

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
