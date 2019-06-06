from trader.lib.MovingTimeSegment.MTSCrossover2 import MTSCrossover2

class MTSCrossAngle(object):
    def __init__(self, ma1=None, ma2=None):
        self.ma1 = ma1
        self.ma2 = ma2
        self.ma1_result = 0
        self.ma2_result = 0
        self.cross = MTSCrossover2()
        self.cross_up_value = 0
        self.cross_up_ts = 0
        self.last_cross_up_value = 0
        self.last_cross_up_ts = 0
        self.cross_down_value = 0
        self.cross_down_ts = 0
        self.last_cross_down_value = 0
        self.last_cross_down_ts = 0

    def update(self, value=0, ma1_result=0, ma2_result=0, ts=0):
        if ma1_result and ma2_result:
            self.ma1_result = ma1_result
            self.ma2_result = ma2_result
        else:
            self.ma1_result = self.ma1.update(value)
            self.ma2_result = self.ma2.update(value)

        self.cross.update(self.ma1_result, self.ma2_result, ts)
        if self.cross.crossup_detected():
            self.last_cross_up_value = self.cross_up_value
            self.last_cross_up_ts = self.cross_up_ts
            self.cross_up_value = self.cross.crossup_value
            self.cross_up_ts = self.cross.crossup_ts
        elif self.cross.crossdown_detected():
            self.last_cross_down_value = self.cross_down_value
            self.last_cross_down_ts = self.cross_down_ts
            self.cross_down_value = self.cross.crossdown_value
            self.cross_down_ts = self.cross.crossdown_ts
