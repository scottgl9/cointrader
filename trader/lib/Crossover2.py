# crossover detection

class Crossover2(object):
    def __init__(self, window=12):
        self.window = window
        self.values1 = []
        self.values2 = []
        self.age = 0
        self.values_under = False
        self.values_over = False
        self.crossup = False
        self.crossdown = False

    def update(self, value1, value2):
        if len(self.values1) < self.window or len(self.values2) < self.window:
            self.values1.append(float(value1))
            self.values2.append(float(value2))
        else:
            self.values1[int(self.age)] = float(value1)
            self.values2[int(self.age)] = float(value2)
            if self.values_under and min(self.values1) > max(self.values2):
                self.values_under = False
                self.crossup = True
            elif self.values_over and max(self.values1) < min(self.values2):
                self.values_over = False
                self.crossdown = True
            elif not self.values_under and not self.values_over:
                if max(self.values1) < min(self.values2):
                    self.values_under = True
                elif min(self.values1) > max(self.values2):
                    self.values_over = True

        self.age = (self.age + 1) % self.window

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

