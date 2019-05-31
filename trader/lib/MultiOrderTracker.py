# for tracking multiple buy orders


class MultiOrderTracker(object):
    def __init__(self, sig_id=0, max_count=1):
        self.max_count = max_count
        self.sig_id = sig_id
        self.sigoids = []
        self.current_sig_oid = 1
        self.multi_order_entries = {}

    def clear(self):
        self.sigoids = []
        self.current_sig_oid = 1
        self.multi_order_entries = {}

    def get_sigoids(self):
        return self.sigoids

    def add(self, buy_price, buy_size):
        if len(self.sigoids) >= self.max_count:
            return False

        entry = MultiOrderEntry(buy_price, buy_size, self.current_sig_oid)
        self.multi_order_entries[self.current_sig_oid] = entry
        self.sigoids.append(self.current_sig_oid)
        self.current_sig_oid += 1
        return True

    def get_price_by_sigoid(self, sigoid):
        if sigoid not in self.multi_order_entries.keys():
            return None
        return self.multi_order_entries[sigoid].buy_price

    def get_size_by_sigoid(self, sigoid):
        if sigoid not in self.multi_order_entries.keys():
            return None
        return self.multi_order_entries[sigoid].buy_size

    def remove_by_signoid(self, sigoid):
        if sigoid in self.multi_order_entries.keys():
            del self.multi_order_entries[sigoid]
            return True
        return False


class MultiOrderEntry(object):
    def __init__(self, buy_price, buy_size, sig_oid):
        self.buy_price = buy_price
        self.buy_size = buy_size
        self.sig_oid = sig_oid
