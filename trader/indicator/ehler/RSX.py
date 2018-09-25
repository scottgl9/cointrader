# Corrected RSX
# https://www.prorealcode.com/prorealtime-indicators/corrected-rsx/
class RSX(object):
    def __init__(self, period=14):
        self.period = period
        self.f0 = 0
        self.f8 = 0
        self.f18 = 0
        self.f20 = 0
        self.f28 = 0
        self.f30 = 0
        self.f38 = 0
        self.f40 = 0
        self.f48 = 0
        self.f50 = 0
        self.f58 = 0
        self.f60 = 0
        self.f68 = 0
        self.f70 = 0
        self.f78 = 0
        self.f80 = 0
        self.f88 = 0
        self.f90 = 0
        self.irsi = 0

    def update(self, close):
        Len = self.period
        smallRsiValue = 0.0000000000000001
        rsiprice = float(close)

        v14 = 0
        v20 = 0
        if self.f90 == 0.0:
            self.f90 = 1.0
            self.f0 = 0.0
            if Len - 1 >= 5:
                self.f88 = Len - 1.0
            else:
                self.f88 = 5.0
            self.f8 = 100.0 * (rsiprice)
            self.f18 = 3.0 / (Len + 2.0)
            self.f20 = 1.0 - self.f18
        else:
            if self.f88 <= self.f90:
                self.f90 = self.f88 + 1
            else:
                self.f90 = self.f90 + 1

            self.f10 = self.f8
            f8 = 100 * float(close)
            v8 = f8 - self.f10
            self.f28 = self.f20 * self.f28 + self.f18 * v8
            self.f30 = self.f18 * self.f28 + self.f20 * self.f30
            vC = self.f28 * 1.5 - self.f30 * 0.5
            self.f38 = self.f20 * self.f38 + self.f18 * vC
            self.f40 = self.f18 * self.f38 + self.f20 * self.f40
            v10 = self.f38 * 1.5 - self.f40 * 0.5
            self.f48 = self.f20 * self.f48 + self.f18 * v10
            self.f50 = self.f18 * self.f48 + self.f20 * self.f50
            v14 = self.f48 * 1.5 - self.f50 * 0.5
            self.f58 = self.f20 * self.f58 + self.f18 * abs(v8)
            self.f60 = self.f18 * self.f58 + self.f20 * self.f60
            v18 = self.f58 * 1.5 - self.f60 * 0.5
            self.f68 = self.f20 * self.f68 + self.f18 * v18

            self.f70 = self.f18 * self.f68 + self.f20 * self.f70
            v1C = self.f68 * 1.5 - self.f70 * 0.5
            self.f78 = self.f20 * self.f78 + self.f18 * v1C
            self.f80 = self.f18 * self.f78 + self.f20 * self.f80
            v20 = self.f78 * 1.5 - self.f80 * 0.5

            if (self.f88 >= self.f90) and (f8 != self.f10):
                f0 = 1.0

            if (self.f88 == self.f90) and (self.f0 == 0.0):
                self.f90 = 0.0

        if (self.f88 < self.f90) and (v20 > smallRsiValue):
            v4 = (v14 / v20 + 1.0) * 50.0
            if v4 > 100.0:
                v4 = 100.0
            if v4 < 0.0:
                v4 = 0.0
        else:
            v4 = 50.0

        self.irsi = v4

        # Corrected function
        #if barindex > self.period:
        #    n = self.period
        #    SA = irsi
        #    v1 = SQUARE(STD[n](SA))
        #    v2 = SQUARE(CA[1] - SA)
        #    if v2 < v1:
        #        k = 0
        #    else:
        #        k = 1 - v1 / v2
        #        CA = CA[1] + K * (SA - CA[1])
