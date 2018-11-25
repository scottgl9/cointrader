# crossover detection
# 1) detect if values1 crosses from below to above values2 (crossup)
# 2) detect if values1 crosses from above to below values2 (crossdown)


class Crossover2(object):
    def __init__(self, window=12):
        self.window = window
        self.values1 = []
        self.values2 = []
        self.age = 0
        self.last_age = 0
        self.values_under = False
        self.values_over = False
        self.crossup = False
        self.crossdown = False

        # optimize check for min and max of self.values1
        self.values1_min_value = 0
        self.values1_min_age = 0
        self.values1_max_value = 0
        self.values1_max_age = 0

        # optimize check for min and max of self.values2
        self.values2_min_value = 0
        self.values2_min_age = 0
        self.values2_max_value = 0
        self.values2_max_age = 0

    def update(self, value1, value2):
        if len(self.values1) < self.window or len(self.values2) < self.window:
            self.values1.append(float(value1))
            self.values2.append(float(value2))
        else:
            self.values1[int(self.age)] = float(value1)
            self.values2[int(self.age)] = float(value2)
            self.update_values1_min_max(float(value1))
            self.update_values2_min_max(float(value2))

            if self.values_under and self.values1_min_value > self.values2_max_value:
                # values1 in window were under values2, now all values1 over values2
                self.values_under = False
                self.crossup = True
            elif self.values_over and self.values1_max_value < self.values2_min_value:
                # values1 in window were over values2, now all values1 under values2
                self.values_over = False
                self.crossdown = True
            elif not self.values_under and not self.values_over:
                if self.values1_max_value < self.values2_min_value:
                    # all of values1 under values2
                    self.values_under = True
                elif self.values1_min_value > self.values2_max_value:
                    # all of values1 over values2
                    self.values_over = True

            self.last_age = self.age
            self.age = (self.age + 1) % self.window


    def update_values1_min_max(self, value):
        #self.values2_min_value = min(self.values2)
        #self.values2_max_value = max(self.values2)
        #return

        if self.values1_min_value == 0 or self.values1_max_value == 0:
            self.values1_min_value = min(self.values1)
            self.values1_max_value = max(self.values1)
            self.values1_min_age = 0
            self.values1_max_age = 0
            return

        if value <= self.values1_min_value:
            self.values1_min_value = value
            self.values1_min_age = 0
            self.values1_max_age += 1
        elif value >= self.values1_max_value:
            self.values1_max_value = value
            self.values1_max_age = 0
            self.values1_min_age += 1
        else:
            self.values1_min_age += 1
            self.values1_max_age += 1

        if self.values1_min_age >= self.window-1:
            self.values1_min_value = min(self.values1)
            self.values1_min_age += 1

        if self.values1_max_age >= self.window-1:
            self.values1_max_value = max(self.values1)
            self.values1_max_age += 1


    def update_values2_min_max(self, value):
        #self.values2_min_value = min(self.values2)
        #self.values2_max_value = max(self.values2)
        #return

        if self.values2_min_value == 0 or self.values2_max_value == 0:
            self.values2_min_value = min(self.values2)
            self.values2_max_value = max(self.values2)
            self.values2_min_age = 0
            self.values2_max_age = 0
            return

        if value <= self.values2_min_value:
            self.values2_min_value = value
            self.values2_min_age = 0
            self.values2_max_age += 1
        elif value >= self.values2_max_value:
            self.values2_max_value = value
            self.values2_max_age = 0
            self.values2_min_age += 1
        else:
            self.values2_min_age += 1
            self.values2_max_age += 1

        if self.values2_min_age >= self.window-1:
            self.values2_min_value = min(self.values2)
            self.values2_min_age += 1

        if self.values2_max_age >= self.window-1:
            self.values2_max_value = max(self.values2)
            self.values2_max_age += 1


    # detect if value1 crosses up over value2
    def crossup_detected(self, clear=True):
        result = False
        if self.crossup:
            result = True
            if clear:
                self.crossup = False
        return result

    # detect if values1 crossed down under values2
    def crossdown_detected(self, clear=True):
        result = False
        if self.crossdown:
            result = True
            if clear:
                self.crossdown = False
        return result

    def clear(self):
        self.crossup = False
        self.crossdown = False
