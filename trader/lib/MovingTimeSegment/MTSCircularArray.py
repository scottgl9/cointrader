# Moving Time Segment (MTS) Dynamic Virtual Size Circular Array
# max_win_size must be >= win_secs


class MTSCircularArray(object):
    def __init__(self, win_secs=60, max_win_size=90, minmax=True):
        self.max_win_size = max_win_size
        self.win_secs = win_secs
        self.win_secs_ts = 1000 * self.win_secs
        self.minmax = minmax
        self._values = [None] * self.max_win_size
        self._timestamps = [None] * self.max_win_size
        self.current_size = 0
        self.end_age = 0
        self.start_age = 0
        self.age = 0
        self._min_value = 0
        self._min_age = 0
        self._max_value = 0
        self._max_age = 0
        self._sum = 0

    def __len__(self):
        return self.current_size

    # allow us to index CircularArray like a regular array
    def __getitem__(self, key):
        if not self.current_size and key > self.end_age:
            raise KeyError("index {} > {}".format(key, self.end_age))
        elif key > self.current_size:
            raise KeyError("index {} > {}".format(key, self.current_size))
        return self.get_value(key)

    def __setitem__(self, key, value):
        if not self.current_size and key > self.end_age:
            raise KeyError("index {} > {}".format(key, self.end_age))
        elif key > self.current_size:
            raise KeyError("index {} > {}".format(key, self.current_size))
        self.set_value(key, value)

    def reset(self):
        self._values = [None] * self.max_win_size
        self._timestamps = [None] * self.max_win_size
        self.start_age = 0
        self.end_age = 0
        self.age = 0
        self.current_size = 0
        self._min_value = 0
        self._min_age = 0
        self._max_value = 0
        self._max_age = 0
        self._sum = 0

    def length(self):
        return self.__len__()

    def empty(self):
        return self.__len__() == 0

    def full(self):
        return self.__len__() == self.max_win_size

    # Add value to circular array
    def add(self, value, ts):
        if self.minmax:
            if not self.min_value or value < self.min_value:
                self._min_value = value
                self._min_age = 0
            else:
                self._min_age += 1

            if value > self.max_value:
                self._max_value = value
                self._max_age = 0
            else:
                self._max_age += 1

        if self.current_size:
            self._sum -= self._values[int(self.age)]

        self._sum += value
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

        if self.minmax and self.current_size:
            if self._min_age > self.current_size:
                age = self.start_age
                min_age = 0
                min_value = 0
                for i in range(0, self.current_size):
                    if not min_value or self._values[age] < min_value:
                        min_value = self._values[age]
                        min_age = age
                    age = (age + 1) % self.current_size
                self._min_value = min_value
                self._min_age = min_age
            if self._max_age > self.current_size:
                age = self.start_age
                max_age = 0
                max_value = 0
                for i in range(0, self.current_size):
                    if max_age < self._values[age]:
                        max_value = self._values[age]
                        max_age = age
                    age = (age + 1) % self.current_size
                self._max_value = max_value
                self._max_age = age

    def start_index(self):
        return self.start_age

    def last_index(self):
        return self.end_age

    def values(self, ordered=True):
        if not ordered:
            if self.current_size:
                return self._values[:self.current_size]
            else:
                return self._values[:self.end_age]

        age = self.start_age
        if self.current_size:
            size = self.current_size
        else:
            size = self.age

        result = [None] * size
        for i in range(0, size):
            result[i] = self._values[int(age)]
            age = (age + 1) % size
        return result

    def timestamps(self, ordered=True):
        if not ordered:
            if self.current_size:
                return self._timestamps[:self.current_size]
            else:
                return self._timestamps[:self.end_age]

        age = self.start_age
        if self.current_size:
            size = self.current_size
        else:
            size = self.age

        result = [None] * size
        for i in range(0, size):
            result[i] = self._timestamps[int(age)]
            age = (age + 1) % size
        return result

    def get_value(self, index):
        if self.current_size:
            pos = (self.start_age + index) % self.current_size
        else:
            pos = index
        return self._values[pos]

    def set_value(self, index, value):
        pos = (self.start_age + index) % self.current_size
        self._values[pos] = value

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

    def min_value(self):
        return self._min_value

    def max_value(self):
        return self._max_value

    def min_value_ts(self):
        return self._timestamps[self._min_age]

    def max_value_ts(self):
        return self._timestamps[self._max_age]
