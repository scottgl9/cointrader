# get the average of multiple moving average (MAs) and return result


class MAAvg(object):
    def __init__(self):
        self.ma_list = []
        self.result = 0

    def add(self, ma):
        self.ma_list.append(ma)

    def update(self, ma_list=None):
        sum = 0
        if not ma_list:
            ma_list = self.ma_list
        ma_count = len(ma_list)
        if not ma_count:
            return self.result
        for ma in ma_list:
            if ma.result == 0:
                self.result = 0
                return self.result
            sum += float(ma.result)
        self.result = sum / ma_count
        return self.result
