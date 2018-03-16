from trader.indicator.SMA import SMA

class DiffWindow:
    def __init__(self, window):
        self.window = window
        self.values = []
        self.diff_values = []
        self.last_value = 0.0
        self.age = 0

    def update(self, value):
        diff_value = 0.0
        if len(self.diff_values) < self.window:
            if self.last_value != 0.0:
                diff_value = float(value) - self.last_value
                self.diff_values.append(diff_value)
                self.values.append(float(value))
        else:
            diff_value = float(value) - self.last_value
            self.diff_values[int(self.age)] = diff_value
            self.values[int(self.age)] = float(value)

        self.age = (self.age + 1) % self.window
        self.last_value = value
        return diff_value

    def get_max_value(self):
        max_value = 0.0
        for value in self.values:
            if value > max_value: max_value = value
        return max_value

    def get_min_value(self):
        min_value = 0.0
        for value in self.values:
            if min_value == 0.0:
                min_value = value
            elif value < min_value: min_value = value
        return min_value

    # find the number of positive changes, and the number of negative changes
    # now compute the sum of the positions for positive changes, then compute the sum
    # of the positions for negative changes. Basically we are trying to determine the average position
    # of positive changes versus the average position of negative changes
    def count_diffs(self):
        if len(self.diff_values) < self.window:
            return 0, 0, 0.0, 0.0, 0, 0, 0.0, 0.0
        pavg = 0.0
        navg = 0.0
        pcount = 0
        ncount = 0
        ratedeccount = 0
        rateinccount = 0
        ratedecavg = 0.0
        rateincavg = 0.0
        age = self.age
        count = 0
        last_value = 0.0
        while age != (self.age - 1) % self.window:
            value = round(self.diff_values[age], 4)
            if value > 0.0:
                pcount += 1
                pavg += float(count)
            elif value < 0.0:
                ncount += 1
                navg += float(count)

            if abs(last_value) < abs(value):
                rateinccount += 1
                rateincavg += float(count)
            elif abs(last_value) > abs(value):
                ratedeccount += 1
                ratedecavg += float(count)

            last_value = value
            age = (age + 1) % self.window
            count += 1
        pavg /= self.window
        navg /= self.window
        ratedecavg /= self.window
        rateincavg /= self.window
        return pcount, ncount, pavg, navg, rateinccount, ratedeccount, rateincavg, ratedecavg

    def detect_valley(self):
        pcount, ncount, pavg, navg, rateinccount, ratedeccount, rateincavg, ratedecavg = self.count_diffs()
        #if positive_count != 0 and negative_count != 0 and positive_count < 2 * negative_count and avg_negative < avg_positive:
        #if pcount != 0 and ncount != 0 and navg < pavg:
        if ncount > (self.window / 2) and ratedeccount > (self.window / 2):
            return True
        return False

    def detect_peak(self):
        pcount, ncount, pavg, navg, rateinccount, ratedeccount, rateincavg, ratedecavg = self.count_diffs()
        #if positive_count != 0 and negative_count != 0 and 2 * positive_count > negative_count and avg_negative > avg_positive:
        #if pcount != 0 and ncount != 0 and navg> avg_positive:
        if pcount > (self.window / 2) and ratedeccount > (self.window / 2):
            return True
        return False

    def detect_rising(self):
        pcount, ncount, avg_positive, avg_negative, rateinccount, ratedeccount, rateincavg, ratedecavg = self.count_diffs()
        #if positive_count != 0 and negative_count != 0 and 2 * positive_count > negative_count and avg_negative > avg_positive:
        if pcount > int(float((self.window) * 0.9)):# and avg_negative < (self.window / 4.0):
            return True
        return False

    def detect_falling(self):
        pcount, ncount, avg_positive, avg_negative, rateinccount, ratedeccount, rateincavg, ratedecavg = self.count_diffs()
        #if positive_count != 0 and negative_count != 0 and 2 * positive_count > negative_count and avg_negative > avg_positive:
        if ncount > int(float((self.window) * 0.9)):# and avg_positive < (self.window / 4.0):
            return True
        return False