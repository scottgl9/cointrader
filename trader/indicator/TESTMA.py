# idea I have for smoothing a moving average
from trader.lib.CircularArray import CircularArray

class TESTMA(object):
    def __init__(self, segment, window):
        self.window = window
        self.segment = segment
        self.values = CircularArray(window=window)
        self.segment_values = []
        self.age = 0
        self.segment_age = 0
        self.result = 0
        self.direction = 0
        self.start_minimum = 0
        self.last_minimum = 0
        self.last_maximum = 0
        self.minimum_age = 0

    def update(self, value):
            self.values.add(float(value))

            seg1 = self.values[:self.segment]
            seg2 = self.values[-self.segment:]
            minimum = min(min(seg1), min(seg2))
            maximum = max(max(seg1), max(seg2))

            if self.direction == -1 and minimum < self.last_minimum:
                self.last_minimum = minimum
            elif self.direction == 1 and minimum > self.last_minimum:
                self.last_minimum = minimum
            else:
                # start new segment and return old segment
                if min(seg1) >= min(seg2):
                    self.direction = -1
                elif min(seg1) < min(seg2):
                    self.direction = 1

                values = []

                if self.last_minimum != 0 and self.minimum_age != 0:
                    slope = (minimum - self.start_minimum) / self.minimum_age

                    for i in range(0, self.minimum_age):
                        values.append(i * slope + self.start_minimum)

                    print(self.direction, self.last_minimum, min(seg1), min(seg2))

                self.last_minimum = minimum
                self.start_minimum = minimum
                self.minimum_age = 0

                return values

        self.minimum_age += 1
        self.age = (self.age + 1) % self.window

        return []
