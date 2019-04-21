# NULL indicator, returns price with no operations
from .IndicatorBase import IndicatorBase


class NULL(IndicatorBase):
    def __init__(self):
        IndicatorBase.__init__(self, use_close=True)
        self.result = 0

    def update(self, value, ts=0):
        self.result = value
        return self.result
