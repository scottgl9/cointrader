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

    def add_cache(self, id):
        self.cache_list[id] = {}

    def remove_cache(self, id):
        if self.empty():
            return

        if id not in self.cache_list:
            return

        del self.cache_list[id]

    def add_result_to_cache(self, id, ts, result):
        if not self.id_in_cache(id):
            return False

        self.cache_list[id][ts] = result
