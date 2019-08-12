# Market Meanness Index (MMI
# https://financial-hacker.com/the-market-meanness-index/#more-250
from trader.lib.struct.IndicatorBase import IndicatorBase
from trader.indicator.MovingMedian import MovingMedian


# // implementation in C
# double MMI(double *Data,int Length)
# {
#   double m = Median(Data,Length);
#   int i, nh=0, nl=0;
#   for(i=1; i<Length; i++) {
#     if(Data[i] > m && Data[i] > Data[i-1]) // mind Data order: Data[0] is newest!
#       nl++;
#     else if(Data[i] < m && Data[i] < Data[i-1])
#       nh++;
#   }
#   return 100.*(nl+nh)/(Length-1);
# }


class MMI(IndicatorBase):
    def __init__(self, window=10):
        IndicatorBase.__init__(self, use_close=True)
        self.window = window
        self.mm = MovingMedian(window=self.window)
        self.values = []
        self.age = 0
        self.result = 0

    def update(self, close):
        self.mm.update(close)
        if len(self.values) < self.window:
            self.values.append(float(close))
        else:
            self.values[int(self.age)] = float(close)
            self.age = (self.age + 1) % self.window
            prev_age = self.age
            age = (self.age + 1) % self.window
            nh = 0
            nl = 0
            for i in range(0, self.window):
                if self.values[age] > self.mm.result and self.values[age] > self.values[prev_age]:
                    nl += 1
                elif self.values[age] < self.mm.result and self.values[age] < self.values[prev_age]:
                    nh += 1
                prev_age = age
                age = (age + 1) % self.window
            self.result = 100.0 * float(nl + nh) / float(self.window - 1)
        return self.result
