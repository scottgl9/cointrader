class CircularArray(object):
    def __init__(self, window):
        self.window = window
        self.carray = []
        self.last_age = 0
        self.age = 0

    def __len__(self):
        return len(self.carray)

    def full(self):
        return len(self.carray) == self.window

    def add(self, value):
        if len(self.carray) < self.window:
            self.carray.append(float(value))
        else:
            self.carray[int(self.age)] = float(value)

        self.last_age = self.age
        self.age = (self.age + 1) % self.window

    def first(self):
        if len(self.carray) == 0:
            return None
        if len(self.carray) < self.window:
            return self.carray[0]
        else:
            return self.carray[int(self.age)]

    def last(self):
        if len(self.carray) == 0:
            return None
        return self.carray[int(self.last_age)]

    def values(self):
        return self.carray

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
