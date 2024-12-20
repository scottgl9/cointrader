import os
import json
from trader.account.CryptoAccountBaseInfo import CryptoAccountBaseInfo
from trader.lib.struct.Order import Order
from trader.lib.struct.AssetInfo import AssetInfo
from trader.lib.struct.Exchange import Exchange

class AccountRobinhoodInfo(CryptoAccountBaseInfo):
    def __init__(self, client, simulate=False, logger=None):
        self.client = client
        self.simulate = simulate
        self.logger = logger
        self.exchange_type = Exchange.EXCHANGE_ROBINHOOD
        self.exchange_name = Exchange.name(self.exchange_type)
        self.exchange_info_file = "{}_info.json".format(self.exchange_name)
        self.info_all_pairs = {}
        self.info_all_assets = {}
        self._exchange_pairs = None
        # hourly db column names
        self.hourly_cnames = ['ts', 'low', 'high', 'open', 'close', 'volume']
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

    def get_account_mode(self):
        return self._account_mode

    def set_account_mode(self, account_mode):
        self._account_mode = account_mode

    def get_ticker_id(self, symbol):
        try:
            info = self.get_info_all_pairs()[symbol]
            return info['id']
        except KeyError:
            return ''

    def get_trade_fee(self):
        return self.trade_fee

    def get_currencies(self):
        return self.currencies

    def get_currency_trade_pairs(self):
        return self.currency_trade_pairs

    def get_info_all_pairs(self):
        return self.info_all_pairs

    def get_info_all_assets(self):
        return self.info_all_assets

    def format_ts(self, ts):
        return int(ts)

    def ts_to_seconds(self, ts):
        return float(ts)

    # returns true if this ts is an hourly ts
    def is_hourly_ts(self, ts):
        hourly_ts = self.get_hourly_ts(ts)
        return int(ts) == hourly_ts

    # set minutes and seconds components of timestamp to zero
    def get_hourly_ts(self, ts):
        #dt = datetime.utcfromtimestamp(self.ts_to_seconds(ts)).replace(minute=0, second=0)
        #return int(self.seconds_to_ts(time.mktime(dt.timetuple())))
        return int(self.ts_to_seconds(ts) / 3600.0) * 3600

    def seconds_to_ts(self, seconds):
        return float(seconds)

    def hours_to_ts(self, hours):
        return float(hours * 3600)

    def get_watchlist_names(self):
        result = []
        w = self.client.get_all_watchlists()
        for r in w['results']:
            result.append(r['display_name'])
        return result

    def get_symbol_from_url(self, url):
        r = self.client.get_instrument_by_url(url)
        return r['symbol']

    # get list of watchlist stock symbols
    def get_watched_symbols(self, names=None):
        result = []

        if not names:
            names = self.get_watchlist_names()

        mode = self.get_account_mode()

        for name in names:
            wl = self.client.get_watchlist_by_name(name=name)
            for w in wl['results']:
                if mode == Exchange.ACCOUNT_MODE_CRYPTO:
                    if w['object_type'] != 'currency_pair':
                        continue
                elif mode == Exchange.ACCOUNT_MODE_STOCKS:
                    if w['object_type'] != 'instrument':
                        continue
                if w['symbol'] not in result:
                    result.append(w['symbol'])
        return result

    # For simulation: load exchange info from file, or call get_exchange_info() and save to file
    def load_exchange_info(self):
        if not self.simulate and os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            self.info_all_pairs = info['pairs']
            self.info_all_assets = info['assets']
            return

        print(self.exchange_info_file)
        if not os.path.exists(self.exchange_info_file):
            info = self.get_exchange_info()
            with open(self.exchange_info_file, 'w') as f:
                json.dump(info, f, indent=4)
        else:
            info = json.loads(open(self.exchange_info_file).read())
        self.info_all_pairs = info['pairs']
        self.info_all_assets = info['assets']

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
        if not self.info_all_assets:
            self.load_exchange_info()
        try:
            result = self.info_all_assets[name]
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
            base_precision = info['base_precision']
            currency_precision = info['currency_precision']
        except KeyError:
            base_precision = 8
            currency_precision = 8

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
                           base_precision=base_precision,
                           currency_precision=currency_precision,
                           orderTypes=orderTypes
                           )
        return result

    def get_asset_info_dict(self, symbol=None, base=None, currency=None, field=None):
        if not self.info_all_pairs:
            self.load_exchange_info()

        if not symbol:
            symbol = self.make_ticker_id(base, currency)

        if not self.info_all_pairs or symbol not in self.info_all_pairs.keys():
            self.logger.warning("symbol {} not found in assets".format(symbol))
            return None
        if field:
            if field not in self.info_all_pairs[symbol]:
                self.logger.warning("field {} not found in assets for symbol {}".format(field, symbol))
                return None
            return self.info_all_pairs[symbol][field]
        return self.info_all_pairs[symbol]
