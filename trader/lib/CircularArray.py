class CircularArray(object):
    def __init__(self, window):
        self.window = window
        self.carray = []
        self.last_age = 0
        self.age = 0

    def __len__(self):
        return len(self.carray)

    def add(self, value):
        if len(self.carray) < self.window:
            self.carray.append(value)
        else:
            self.carray[int(self.age)] = value

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

    def first_index(self):
        if len(self.carray) < self.window:
            return 0
        else:
            return self.age

    def last_index(self):
        return self.last_age

    def values_by_range(self, start=0, end=-1):
        values = []
        age = self.last_age
        while age != self.age:
            values.append(self.carray[int(age)])
            age = (age + 1) % self.window

        return values[start:end]
