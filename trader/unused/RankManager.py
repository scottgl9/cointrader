
class RankManager(object):
    def __init__(self):
        self.value_by_symbol = {}

    def update(self, symbol, value):
        self.value_by_symbol[symbol] = value

    def rank_ascending(self):
        return sorted(self.value_by_symbol.iteritems(), key=lambda (k, v): (v, k))

    def rank_descending(self):
        return sorted(self.value_by_symbol.iteritems(), key=lambda (k, v): (v, k), reverse=True)

    def rank_descending_top(self, cutoff=3):
        rank = self.rank_descending()
        #cutoff = len(rank) / 8
        if len(rank) > cutoff: rank = rank[0:cutoff]
        return rank

    def rank_descending_bottom(self, cutoff=3):
        rank = self.rank_descending()
        #cutoff = len(rank) / 8
        if len(rank) > cutoff: rank = rank[-cutoff:]
        return rank

    def rank(self, symbol):
        ranks = self.rank_descending()
        pos = 0
        for s, v in ranks:
            if s == symbol:
                break
            pos += 1
        return pos
