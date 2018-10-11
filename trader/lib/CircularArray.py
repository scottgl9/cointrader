class CircularArray(object):
    def __init__(self, window, dne=None, reverse=True):
        self.window = window
        self.carray = []
        # if value at index doesn't exist, return value set in dne
        self.dne = dne
        # reverse indexing if class treated like an array
        self.reverse = reverse
        self.last_age = 0
        self.age = 0

    def __len__(self):
        return len(self.carray)

    # allow us to index CircularArray like a regular array with reverse indexing
    def __getitem__(self, key):
        if self.reverse:
            return self.last(index=key)
        else:
            return self.first(index=key)

    def __setitem__(self, key, value):
        if self.reverse:
            self.last_set(key, value)
        else:
            self.first_set(key, value)

    def length(self):
        return len(self.carray)

    def empty(self):
        return len(self.carray) == 0

    def full(self):
        return len(self.carray) == self.window

    # Add value to circular array
    def add(self, value):
        if len(self.carray) < self.window:
            self.carray.append(value)
        else:
            self.carray[int(self.age)] = value

        self.last_age = self.age
        self.age = (self.age + 1) % self.window

    # forward indexing: first(0) = first added, first(1) = second added, etc
    def first(self, index=0):
        if len(self.carray) == 0:
            return self.dne

        if len(self.carray) < self.window:
            if index >= len(self.carray):
                return self.dne
            return self.carray[index]
        else:
            age = int(self.age)
            if index != 0:
                age = (age + index) % self.window
            return self.carray[age]

    # reverse indexing: last(0) = last added, last(1) = second to last added, etc
    def last(self, index=0):
        if len(self.carray) == 0:
            return self.dne

        if len(self.carray) < self.window:
            if index >= len(self.carray):
                return self.dne

        age = int(self.last_age)

        if index != 0:
            while index > 0:
                index -= 1
                age -= 1
                if age < 0:
                    age = self.window - 1

        return self.carray[age]

    # forward indexing: first(0) = first added, first(1) = second added, etc
    def first_set(self, index=0, value=0):
        if len(self.carray) == 0:
            return

        if len(self.carray) < self.window:
            if index >= len(self.carray):
                return self.dne
            self.carray[index] = value
            return
        else:
            age = int(self.age)
            if index != 0:
                age = (age + index) % self.window
            self.carray[age] = value
            return

    # reverse indexing: last(0) = last added, last(1) = second to last added, etc
    def last_set(self, index=0, value=0):
        if len(self.carray) == 0:
            return

        if len(self.carray) < self.window:
            if index >= len(self.carray):
                return

        age = int(self.last_age)

        if index != 0:
            while index > 0:
                index -= 1
                age -= 1
                if age < 0:
                    age = self.window - 1

        self.carray[age] = value

    # return un-ordered values
    def values(self):
        return self.carray

    # return as ordered array of values from oldest to newest
    def values_ordered(self):
        values = []
        age = self.age
        while age != self.last_age:
            values.append(self.carray[int(age)])
            age = (age + 1) % self.window
        return values

    def first_index(self):
        if len(self.carray) < self.window:
            return 0
        else:
            return self.age

    def last_index(self):
        return self.last_age

    def values_by_range(self, start=0, end=-1):
        values = self.values_ordered()
        return values[start:end]

    # get value X time slots ago: -1=last, -2=prevous, etc
    def get_value(self, index=-1):
        if not self.full():
            return 0
        age = self.age
        if self.age == 0 and index < 0:
            index += 1
            age = self.window - 1
        age = (age + index) % self.window
        return self.carray[int(age)]

    def min(self):
        return min(self.carray)

    def max(self):
        return max(self.carray)
