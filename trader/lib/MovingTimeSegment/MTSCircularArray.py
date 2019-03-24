# Moving Time Segment (MTS) Dynamic Virtual Size Circular Array
# max_win_size must be >= win_secs


class MTSCircularArray(object):
    def __init__(self, win_secs=60, max_win_size=90):
        self.max_win_size = max_win_size
        self.win_secs = win_secs
        self.win_secs_ts = 1000 * self.win_secs
        self._values = [None] * self.max_win_size
        self._timestamps = [None] * self.max_win_size
        self.current_size = 0
        self.end_age = 0
        self.start_age = 0
        self.age = 0
        self.ts = 0

    def __len__(self):
        return self.current_size

    # allow us to index CircularArray like a regular array with reverse indexing
    # def __getitem__(self, key):
    #     if self.reverse:
    #         return self.last(index=key)
    #     else:
    #         return self.first(index=key)
    #
    # def __setitem__(self, key, value):
    #     if self.reverse:
    #         self.last_set(key, value)
    #     else:
    #         self.first_set(key, value)

    def reset(self):
        self._values = [None] * self.max_win_size
        self._timestamps = [None] * self.max_win_size
        self.start_age = 0
        self.end_age = 0
        self.age = 0
        self.current_size = 0

    def length(self):
        return self.__len__()

    def empty(self):
        return self.__len__() == 0

    def full(self):
        return self.__len__() == self.max_win_size

    # Add value to circular array
    def add(self, value, ts):
        self.ts = ts
        self._values[int(self.age)] = value
        self._timestamps[int(self.age)] = ts

        # if start_age back at index 0, and diff in timestamps >= win_sec_ts,
        # then resize current_size of circular array
        if self.start_age == 0 and (ts - self._timestamps[0]) >= self.win_secs_ts:
            self.current_size = self.age

        # index of most recent value and ts
        self.end_age = self.age

        if self.current_size:
            self.start_age = (self.start_age + 1) % self.current_size
            self.age = (self.age + 1) % self.current_size
        else:
            self.age = (self.age + 1) % self.max_win_size

    def start_index(self):
        return self.start_age

    def last_index(self):
        return self.end_age

    def values(self, ordered=True):
        if not ordered:
            return self._values

        age = self.start_age
        if self.current_size:
            size = self.current_size
        else:
            size = self.max_win_size

        result = [None] * size
        for i in range(0, size):
            result[i] = self._values[int(age)]
            age = (age + 1) % size
        return result

    def first_value(self):
        return self._values[self.start_age]

    def last_value(self):
        return self._values[self.end_age]

    def first_ts(self):
        return self._timestamps[self.start_age]

    def last_ts(self):
        return self._timestamps[self.end_age]

    def set_first(self, value, ts):
        self._values[self.start_age] = value
        self._timestamps[self.start_age] = ts

    def set_last(self, value, ts):
        self._values[self.end_age] = value
        self._timestamps[self.end_age] = ts
