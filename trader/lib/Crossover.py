# crossover detection
# 1) detect if values1 crosses from below to above values2 (crossup)
# 2) detect if values1 crosses from above to below values2 (crossdown)

# pre_window allows an additional window to check before or after crossover
# in addition to window, to verify all values in pre_window were under/over crosspoint
# before crossup/crossdown occurred


class Crossover(object):
    def __init__(self, pre_window=0, window=12, detect_cross_value=False):
        self.window = window
        self.pre_window = pre_window
        self.detect_cross_value = detect_cross_value

        self.values1 = []
        self.values2 = []
        self.pre_values1 = []
        self.pre_values2 = []
        self.pre_age = 0
        self.age = 0
        self.last_age = 0
        self.values_under = False
        self.values_over = False
        # use for detecting the value where crossover took place
        self.values1_under_max_value = 0
        self.values1_over_min_value = 0
        self.crossup = False
        self.crossdown = False
        self.crossup_value = 0
        self.crossdown_value = 0

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
        if len(self.values1) < self.window:
            self.values1.append(float(value1))
            self.values2.append(float(value2))
        else:
            if self.pre_window:
                if len(self.pre_values1) < self.pre_window:
                    self.pre_values1.append(self.values1[int(self.age)])
                    self.pre_values2.append(self.values2[int(self.age)])
                else:
                    self.pre_values1[int(self.pre_age)] = self.values1[int(self.age)]
                    self.pre_values2[int(self.pre_age)] = self.values2[int(self.age)]
                    self.pre_age = (self.pre_age + 1) % self.pre_window

            self.values1[int(self.age)] = float(value1)
            self.values2[int(self.age)] = float(value2)
            self.update_values1_min_max(float(value1))
            self.update_values2_min_max(float(value2))

            if self.values_under and self.values1_min_value > self.values2_max_value:
                # values1 in window were under values2, now all values1 over values2
                self.values_under = False
                self.crossup = True
                if self.detect_cross_value:
                    # estimate the value where the cross-up occurred
                    self.crossup_value = (self.values1_min_value + self.values1_under_max_value) / 2.0
            elif self.values_over and self.values1_max_value < self.values2_min_value:
                # values1 in window were over values2, now all values1 under values2
                self.values_over = False
                self.crossdown = True
                if self.detect_cross_value:
                    # estimate the value where the cross-down occurred
                    self.crossdown_value = (self.values1_max_value + self.values1_over_min_value) / 2.0
            elif not self.values_under and not self.values_over:
                if self.values1_max_value < self.values2_min_value:
                    if self.pre_window:
                        # make sure values1 in pre_window were also under values2
                        if max(self.pre_values1) < min(self.pre_values2):
                            self.values_under = True
                            self.values1_under_max_value = self.values1_max_value
                    else:
                        # all of values1 under values2
                        self.values_under = True
                        self.values1_under_max_value = self.values1_max_value
                elif self.values1_min_value > self.values2_max_value:
                    if self.pre_window:
                        # make sure values1 in pre_window were also over values2
                        if min(self.pre_values1) > max(self.pre_values2):
                            self.values_over = True
                            self.values1_over_min_value = self.values1_min_value
                    else:
                        # all of values1 over values2
                        self.values_over = True
                        self.values1_over_min_value = self.values1_min_value

            self.last_age = self.age
            self.age = (self.age + 1) % self.window


    def update_values1_min_max(self, value):
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
