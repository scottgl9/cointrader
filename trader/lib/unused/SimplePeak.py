# Simple peak detector
class SimplePeak(object):
    def __init__(self, win_left=10, win_right=10):
        self.win_left = win_left
        self.win_right = win_right
        self.values = []
        self.window = self.win_left + self.win_right
        self.age = 0

    def update(self, value):
        if len(self.values) < self.window:
            self.values.append(float(value))
        else:
            if float(value) in self.values:
                return
            self.values[int(self.age)] = float(value)

        self.age = (self.age + 1) % self.window

    def peak(self):
        if len(self.values) < self.window:
            return False

        mid_value = self.values[int(self.win_left)]
        if max(self.values) == mid_value:
            return True

        return False
