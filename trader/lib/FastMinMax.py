# more efficient way to calculate min(values) and max(values) by tracking the maximum and minimums, versus
# just calling min(values) or max(values) for every change in values


# allows for a variable size of values, when values can be removed, but always keeps track of min and max values
class FastMinMax(object):
    def __init__(self):
        self.values = []
        self.min_value = 0
        self.min_value_index = -1
        self.max_value = 0
        self.max_value_index = -1
        self.end_index = -1

    def min(self):
        return self.min_value

    def max(self):
        return self.max_value

    def append(self, value):
        if self.min_value_index == -1 or self.max_value_index == -1:
            self.min_value = value
            self.min_value_index = 0
            self.max_value = value
            self.max_value_index = 0
            self.values.append(value)
            self.end_index += 1
            return

        if value != 0 and self.min_value != 0 and value <= self.min_value:
            self.min_value = value
            self.min_value_index = self.end_index
        elif value >= self.max_value:
            self.max_value = value
            self.max_value_index = self.end_index

        self.end_index += 1

    # remove count items from beginning of self.values
    def remove(self, count):
        if len(self.values) <= count:
            return
        self.min_value_index -= count
        self.max_value_index -= count
        self.end_index -= count

        self.values = self.values[count:]

        if self.min_value_index < 0:
            self.min_value_index = min(xrange(len(self.values)), key=self.values.__getitem__)
            self.min_value = self.values[self.min_value_index]
        elif self.min_value_index > self.end_index:
            self.min_value_index = self.end_index

        if self.max_value_index < 0:
            self.max_value_index = max(xrange(len(self.values)), key=self.values.__getitem__)
            self.max_value = self.values[self.max_value_index]
        elif self.max_value_index > self.end_index:
            self.max_value_index = self.end_index
