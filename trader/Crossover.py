# crossover detection

class Crossover(object):
    def __init__(self):
        self.value1 = 0.0
        self.value2 = 0.0
        self.last_value1 = 0.0
        self.last_value2 = 0.0

    def update(self, value1, value2):
        if self.value1 != 0 and self.value1 != self.last_value1:
            if self.last_value1 == 0 or abs(self.value1 - self.last_value1) / self.last_value1 > 0.001:
                self.last_value1 = self.value1
        if self.value2 != 0 and self.value2 != self.last_value2:
            if self.last_value2 == 0 or abs(self.value2 - self.last_value2) / self.last_value2 > 0.001:
                self.last_value2 = self.value2
        if self.value1 == 0 or self.value1 != value1:
            self.value1 = value1
        if self.value2 == 0 or self.value2 != value2:
            self.value2 = value2

    # detect if value1 crosses up over value2
    def crossup_detected(self):
        if self.value1 == 0.0 or self.last_value1 == 0.0:
            return False
        if self.value2 == 0.0 or self.last_value2 == 0.0:
            return False
        if self.last_value1 < self.value2 < self.value1 and self.value2 > self.last_value2:
            return True
        #if self.last_value2 > self.value1 > self.value2:
        #    return True
        return False

    def crossdown_detected(self):
        if self.value1 == 0.0 or self.last_value1 == 0.0:
            return False
        if self.value2 == 0.0 or self.last_value2 == 0.0:
            return False
        if self.last_value1 > self.value2 > self.value1:
            return True
        #if self.last_value2 < self.value1 < self.value2:
        #    return True
        return False
