# NULL indicator, returns price with no operations

class NULL(object):
    def __init__(self):
        self.result = 0

    def update(self, value, ts=0):
        self.result = value
        return self.result
