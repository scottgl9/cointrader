import os
import json
from .cbpro import AuthenticatedClient, PublicClient
from trader.account.AccountBaseInfo import AccountBaseInfo


class AccountCoinbaseInfo(AccountBaseInfo):
    def __init__(self, client, simulation=False, logger=None, exchange_info_file=None):
        self.client = client
        self.simulate = simulation
        self.logger = logger
        self.exchange_info_file = exchange_info_file
        self.info_all_assets = {}
        self.details_all_assets = {}
        self._exchange_pairs = None
        self.pc = PublicClient()
        self.currencies = ['BTC', 'ETH', 'USDC', 'USD']
        self.currency_trade_pairs = ['ETH-BTC', 'BTC-USDC', 'ETH-USDC', 'BTC-USD', 'ETH-USD']
        self.trade_fee = 0.5 / 100.0

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
        pair_info = self.pc.get_products()
        asset_info = self.pc.get_currencies()
        return self.parse_exchange_info(pair_info, asset_info)

    def parse_exchange_info(self, pair_info, asset_info):
        exchange_info = {}
        pairs = {}
        assets = {}

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
        for info in asset_info:
            name = info['id']
            status = info['status']
            if status == 'online':
                assets[name] = {'disabled': False, 'delisted': False }
            else:
                assets[name] = {'disabled': True, 'delisted': False }

        self._exchange_pairs = []

        for pair in pairs.keys():
            # ignore trade pairs with GBP and EUR currency
            if pair.endswith('GBP') or pair.endswith('EUR'):
                continue
            self._exchange_pairs.append(pair)

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

    def is_asset_available(self, name):
        raise NotImplementedError

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
