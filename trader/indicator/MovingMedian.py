# Moving median algorithm using indexable skiplist
from trader.lib.IndexableSkiplist import IndexableSkiplist


class MovingMedian(object):
    def __init__(self, window):
        self.window = window
        self.mid_index = self.window / 2
        self.skip_list = IndexableSkiplist(win_size=self.window)
        self.values = []
        self.age = 0
        self.result = 0

    def update(self, close):
        if len(self.values) < self.window:
            self.skip_list.insert(float(close))
            self.result = float(close)
        else:
            old_value = self.values[int(self.age)]
            self.values[int(self.age)] = float(close)
            self.skip_list.remove(old_value)
            self.skip_list.insert(float(close))
            self.age = (self.age + 1) % self.window
            self.result = self.skip_list[self.mid_index]

        return self.result
