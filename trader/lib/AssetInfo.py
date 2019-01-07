# holds information about an asset (asset_info.json for reference)


class AssetInfo(object):
    def __init__(self, base=None, currency=None, min_qty=0, min_price=0, base_step_size=0, currency_step_size=0,
                 is_currency_pair=False):
        self.base = base
        self.currency = currency
        self.min_qty = min_qty
        self.min_price = min_price
        self.base_step_size = base_step_size
        self.currency_step_size = currency_step_size
        self.is_currency_pair = is_currency_pair
