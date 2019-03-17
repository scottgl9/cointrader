# double crossover detection
from trader.lib.Crossover import Crossover

class CrossoverDouble(object):
    def __init__(self, window=10):
        self.window = window
        self.cross12 = Crossover(window=window)
        self.cross13 = Crossover(window=window)
        self.crossup = False
        self.crossdown = False

    def update(self, value1, value2, value3):
        self.cross12.update(value1, value2)
        self.cross13.update(value1, value3)

        # values1 crossed up over values3, determine if previously values1 crossed up over values2
        if self.cross13.crossup_detected():
            if self.cross12.crossup_detected():
                self.crossup = True

        # values1 crossed down over valuus3, determine if previously values1 crossed down over values2
        if self.cross13.crossdown_detected():
            if self.cross12.crossdown_detected():
                self.crossdown = True

    # detect if value1 crosses up over value2
    def crossup_detected(self):
        result = False
        if self.crossup:
            result = True
            self.crossup = False
        return result

    def crossdown_detected(self):
        result = False
        if self.crossdown:
            result = True
            self.crossdown = False
        return result
