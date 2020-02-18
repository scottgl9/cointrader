# base account class for handling account information

class AccountBaseInfo(object):
    def load_exchange_info(self):
        pass

    def get_exchange_info(self):
        pass

    def parse_exchange_info(self, pair_info, asset_info):
        pass

    def get_exchange_pairs(self):
        pass

    def is_exchange_pair(self, symbol):
        pass

    def is_asset_available(self, name):
        pass
