# compare multiple moving averages

class MACompare(object):
    def __init__(self, ma_list=None):
        self.ma_list = ma_list
        self.ma_results = None

    def update(self, ma_results=None):
            if not ma_results:
                return

            self.ma_results = ma_results

    def ma_proximity_test(self, percent=0.1):
        if not self.ma_results:
            return False

        for i in range(0, len(self.ma_results) - 1):
            result1 = self.ma_results[i]
            result2 = self.ma_results[i+1]
            if 100.0 * abs(result1 - result2) / result2 > percent:
                return False

        return True
