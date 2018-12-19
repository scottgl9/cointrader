class IndicatorCache(object):
    def __init__(self, symbol):
        self.cache_list = None
        self.cache_counters = {}
        self.symbol = symbol
        self.loaded = False

    def empty(self):
        return not self.cache_list

    def get_cache_list(self):
        return self.cache_list

    def id_in_cache(self, id):
        if id in self.cache_list:
            return True
        return False

    def create_cache(self, id):
        if self.empty():
            self.cache_list = {}

        if 'ts' not in self.cache_list:
            self.cache_list['ts'] = []

        self.cache_list[id] = []

    def remove_cache(self, id):
        if self.empty():
            return

        if id not in self.cache_list:
            return

        del self.cache_list[id]

    def get_result_from_cache(self, id):
        id = str(id)
        counter = self.cache_counters[id]
        result = self.cache_list[id][counter]
        self.cache_counters[id] = counter + 1
        return result

    def add_result_to_cache(self, id, ts, result):
        if not self.id_in_cache(id):
            return False

        if ts not in self.cache_list['ts']:
            self.cache_list['ts'].append(ts)

        self.cache_list[id].append(result)
        return True

    def load_cache_from_db(self, db=None):
        if not db:
            return False

        self.cache_list = {}

        c = db.cursor()
        c.execute("SELECT * FROM {}".format(self.symbol))

        # get column names
        ids = [description[0] for description in c.description]

        for id in ids:
            self.cache_list[id] = []
            self.cache_counters[id] = 0

        for row in c:
            for i in range(0, len(row)):
                self.cache_list[ids[i]].append(row[i])

        self.loaded = True

        return True
