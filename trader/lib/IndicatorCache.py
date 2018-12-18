class IndicatorCache(object):
    def __init__(self):
        self.cache_list = None

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

    def add_result_to_cache(self, id, ts, result):
        if not self.id_in_cache(id):
            return False

        if ts not in self.cache_list['ts']:
            self.cache_list['ts'].append(ts)

        self.cache_list[id].append(result)
        return True
