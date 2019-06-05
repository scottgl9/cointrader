from .Crossover import Crossover

class CrossAngle(object):
    def __init__(self, ma1=None, ma2=None):
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.cross = Crossover(window=10, detect_cross_value=True)

    def update(self, value=0, ts=0, ma1_result=0, ma2_result=0):
        if ma1_result and ma2_result:
            self.ma1_result = ma1_result
            self.ma2_result = ma2_result
        else:
            self.ma1_result = self.ma1.update(value)
            self.ma2_result = self.ma2.update(value)

        self.cross.update(self.ma1_result, self.ma2_result)
