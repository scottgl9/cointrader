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

    def load(self, buy_price, buy_size, sig_oid):
        self.current_sig_oid = sig_oid
        entry = MultiOrderEntry(buy_price, buy_size, self.current_sig_oid)
        self.multi_order_entries[self.current_sig_oid] = entry
        self.sigoids.append(self.current_sig_oid)
        self.current_sig_oid += 1
        return True

    def add(self, buy_price, buy_size, ts=0):
        if len(self.sigoids) >= self.max_count:
            return 0
        result = self.current_sig_oid
        entry = MultiOrderEntry(buy_price=float(buy_price),
                                buy_size=float(buy_size),
                                sig_oid=self.current_sig_oid,
                                last_buy_ts=ts)
        self.multi_order_entries[self.current_sig_oid] = entry
        self.sigoids.append(self.current_sig_oid)
        self.current_sig_oid += 1
        return result

    def mark_buy_completed(self, sigoid):
        try:
            self.multi_order_entries[sigoid].buy_completed = True
        except KeyError:
            return False
        return True

    def get_buy_completed(self, sigoid):
        try:
            result = self.multi_order_entries[sigoid].buy_completed
        except KeyError:
            return False
        return result

    def mark_sell_started(self, sigoid):
        try:
            self.multi_order_entries[sigoid].sell_started = True
        except KeyError:
            return False
        return True

    def get_sell_started(self, sigoid):
        try:
            result = self.multi_order_entries[sigoid].sell_started
        except KeyError:
            return False
        return result

    def get_price_by_sigoid(self, sigoid):
        try:
            result = self.multi_order_entries[sigoid].buy_price
        except KeyError:
            return 0
        return result

    def get_size_by_sigoid(self, sigoid):
        try:
            result = self.multi_order_entries[sigoid].buy_size
        except KeyError:
            return 0
        return result

    def update_price_by_sigoid(self, sigoid, buy_price):
        try:
            self.multi_order_entries[sigoid].buy_price = float(buy_price)
        except KeyError:
            return False
        return True

    def update_size_by_sigoid(self, sigoid, buy_size):
        try:
            self.multi_order_entries[sigoid].buy_size = float(buy_size)
        except KeyError:
            return False
        return True

    # get list of sigoids which are available to sell
    def get_sell_sigoids(self, sell_price, percent=1.0):
        result = []
        for entry in self.multi_order_entries.values():
            if sell_price > entry.buy_price and 100.0 * (sell_price - entry.buy_price) / entry.buy_price >= percent:
                result.append(entry.sig_oid)
        return result

    # get total size that we can sell at percent profit
    def get_total_sell_size(self, sell_price, percent=1.0):
        total_size = 0
        for entry in self.multi_order_entries.values():
            if sell_price > entry.buy_price and 100.0 * (sell_price - entry.buy_price) / entry.buy_price >= percent:
                total_size += entry.buy_size
        return total_size

    # check if buy has already occurred at specified buy_price
    def buy_price_exists(self, buy_price):
        for entry in self.multi_order_entries.values():
            if entry.buy_price == buy_price:
                return True
        return False

    # remove all entries that we can sell at percent profit
    def remove_total_sell_size(self, sell_price, percent=1.0):
        remove_entries = []
        for entry in self.multi_order_entries.values():
            if sell_price > entry.buy_price and 100.0 * (sell_price - entry.buy_price) / entry.buy_price >= percent:
                remove_entries.append(entry)
        for entry in remove_entries:
            self.sigoids.remove(entry.sig_oid)
            del self.multi_order_entries[entry.sig_oid]

    def remove_by_buy_price(self, buy_price):
        completed = False
        remove_entries = []
        for entry in self.multi_order_entries:
            if entry.buy_price == buy_price:
                completed = True
                remove_entries.append(entry)
        for entry in remove_entries:
            self.sigoids.remove(entry.sig_oid)
            del self.multi_order_entries[entry.sig_oid]
        return completed

    def remove_by_sigoid(self, sigoid):
        try:
            del self.multi_order_entries[sigoid]
        except KeyError:
            return False
        return True


class MultiOrderEntry(object):
    def __init__(self, buy_price, buy_size, sig_oid, last_buy_ts=0):
        self.buy_price = buy_price
        self.buy_size = buy_size
        self.buy_completed = False
        self.sell_started = False
        self.sig_oid = sig_oid
        self.last_buy_ts = last_buy_ts
