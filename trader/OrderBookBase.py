class OrderBookBase:
    def __init__(self):
        self.bids_book = {}
        self.asks_book = {}

    def process_update(self, msg):
        pass

    def get_bids_by_range(self, min, max, limit=None):
        count=0
        bids = {}
        for key, value in sorted(self.bids_book.iteritems()):
            if limit and count > limit: break
            count += 1
            if key <= max and key >= min:
                bids[key] = value
        return bids

    def get_bids_distribution_by_range(self, min, max, cutoff=0.0):
        total_amount = 0.0
        bids = self.get_bids_by_range(min, max)
        for bid in bids.values():
            total_amount += float(bid)
        if total_amount == 0.0: return {}
        for key, value in sorted(bids.iteritems()):
            bids[key] = round((float(value) / total_amount) * 100.0, 2)
            if bids[key] <= cutoff: del bids[key]
        return sorted(bids.items())
        #return sorted(bids.iteritems(), key=lambda (k, v): (v, k), reverse=True)

    def get_asks_by_range(self, min, max, limit=None):
        count=0
        asks = {}
        for key, value in sorted(self.asks_book.iteritems()):
            if limit and count > limit: break
            count += 1
            if key <= max and key >= min:
                asks[key] = value
        return asks

    def get_asks_distribution_by_range(self, min, max, cutoff=0.0):
        total_amount = 0.0
        asks = self.get_asks_by_range(min, max)
        for ask in asks.values():
            total_amount += float(ask)
        if total_amount == 0.0: return {}
        for key, value in sorted(asks.iteritems()):
            asks[key] = round((float(value) / total_amount) * 100.0, 2)
            if asks[key] <= cutoff: del asks[key]
        #return sorted(asks.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        return sorted(asks.items())

    def get_diffs_distribution_by_range(self, min, max):
        diffs = {}
        bids = dict(self.get_bids_distribution_by_range(min, max))
        asks = dict(self.get_asks_distribution_by_range(min, max))
        keys = list(set(bids.keys() + asks.keys()))
        for key in keys:
            if key in bids.keys():
                diffs[key] = bids[key]
            else:
                diffs[key] = 0.0
            if key in asks.keys():
                diffs[key] = diffs[key] - asks[key]
        return sorted(diffs.items())

    def get_sorted_bids_book(self, limit=None):
        count = 0
        for key, value in sorted(self.bids_book.iteritems(), key=lambda (k, v): (v, k)):
            if limit and count >= limit: break
            count += 1
            print(key, value)

    def get_sorted_asks_book(self, limit=None):
        count = 0
        for key, value in sorted(self.asks_book.iteritems(), key=lambda (k, v): (v, k)):
            if limit and count >= limit: break
            count += 1
            print(key, value)

    # this algorithm I designed basically does the following:
    # 1) find price in bids and asks that is closest to market_price
    # 2) if the price element closest to market_price will have the highest "weight" in either asks or bids
    # if highest weight in asks, add weights of each weight in bids until the summed weight is >= the weight in asks
    # otherwise if highest weight in bids, add weights of each weight in asks until the summed weight is >= the weight in bids
    # now we save the point at which the summation of weights was >= highest weight
    # this price point determines the maximum amount the price can move if we are only considering open limit orders
    def compute_expected_price_movement(self, market_price):
        bids_book_amount = 0.0
        asks_book_amount = 0.0
        # bids in decending order and asks in ascending order
        bids = sorted(self.get_bids_by_range(market_price - 20.0, market_price + 20.0).items(), reverse=True)
        asks = sorted(self.get_asks_by_range(market_price - 20.0, market_price + 20.0).items())
        price_start = 0.0
        price_end = 0.0
        ask_index = 0.0
        bid_index = 0.0
        weight = 0.0
        resistance = 0.0
        # maximum "obstacle" weight
        oweight = 0.0
        # price with maximum "obstacle" weight
        oprice = 0.0

        if len(bids) == 0: return price_start, price_end, weight, resistance, oprice, oweight
        if len(asks) == 0: return price_start, price_end, weight, resistance, oprice, oweight

        # get start index closest to market price
        for i in range(0, len(asks)):
            if asks[i][0] >= market_price:
                ask_index = i
                break
        for i in range(0, len(bids)):
            if bids[i][0] <= market_price:
                bid_index = i
                break

        # check which side has a higher quantity at the best market price for each
        if asks[ask_index][1] > bids[bid_index][1]:
            amount = 0.0
            price_start = asks[ask_index][0]
            weight = asks[ask_index][1]
            resistance = bids[bid_index][1]
            oprice = price_start
            oweight = resistance
            for bid in bids[bid_index:]:
                amount += bid[1]
                if amount >= asks[ask_index][1]:
                    price_end = bid[0]
                    break
                if bid[1] > oweight:
                    oweight = bid[1]
                    oprice = bid[0]
        elif asks[ask_index][1] < bids[bid_index][1]:
            amount = 0.0
            price_start = bids[bid_index][0]
            weight = bids[bid_index][1]
            resistance = asks[ask_index][1]
            for ask in asks[ask_index:]:
                amount += ask[1]
                if amount >= bids[bid_index][1]:
                    price_end = ask[0]
                    break
                if ask[1] > oweight:
                    oweight = ask[1]
                    oprice = ask[0]

        return price_start, price_end, weight, resistance, oprice, oweight