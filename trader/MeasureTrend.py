from trader.indicator.SMA import SMA
from trader.indicator.EMA import EMA
import numpy as np
from sklearn import datasets, linear_model
import time
from sklearn.metrics import mean_squared_error, r2_score

# IDEA: get range with highest level of oscillation

class MeasureTrend(object):
    def __init__(self, name='BTCUSD', window=50, detect_width=16):
        self.prices = []
        self.last_price = 0.0
        self.sma_prices = []
        self.ts = []
        self.name = name
        self.window = window
        self.detect_width = detect_width
        self.sma = EMA(12)

    def update_price(self, price):
        if self.last_price != 0.0 and price == self.last_price:
            return
        if len(self.prices) > self.window:
            self.prices.pop(0)
            self.sma_prices.pop(0)
            self.ts.pop(0)

        self.prices.append(float(price))
        self.sma_prices.append(self.sma.update(price))
        self.ts.append(float(time.time()))
        self.last_price = price

    def peak_detected(self):
        if len(self.sma_prices) < self.window:
            return False

        for i in range(self.detect_width, len(self.sma_prices) - self.detect_width):
            for j in range(1, self.detect_width):
                if self.sma_prices[i - j] > self.sma_prices[i] or self.sma_prices[i] < self.sma_prices[i + j]:
                    return False
                if self.sma_prices[i-j] > self.sma_prices[i-j+1] or self.sma_prices[i+j-1] < self.sma_prices[i+j]:
                    return False

        return True

    def valley_detected(self):
        if len(self.sma_prices) < self.window:
            return False

        for i in range(self.detect_width, len(self.sma_prices) - self.detect_width):
            for j in range(1, self.detect_width):
                if self.sma_prices[i - j] < self.sma_prices[i] or self.sma_prices[i] > self.sma_prices[i + j]:
                    return False
                if self.sma_prices[i-j] < self.sma_prices[i-j+1] or self.sma_prices[i+j-1] > self.sma_prices[i+j]:
                    return False

        return True


    def compute_linear_regression(self):
        if len(self.sma_prices) < self.window:
            return
        regr = linear_model.LinearRegression()
        x_values = []
        y_values = []
        last_price = 0.0
        for i in range(0, len(self.sma_prices) - 1):
            if last_price == 0.0:
                x_values.append(i)
                y_values.append(self.sma_prices[i])
            last_price = self.sma_prices[i]
        regr.fit(np.array(x_values).reshape(-1, 1), np.array(y_values))

        if regr.coef_ != 0.0:
            print('Coefficients: \n', regr.coef_)

        line = regr.predict(np.array(x_values).reshape(-1, 1))
        print_line = False
        for point in line:
            if point != 0.0:
                print_line = True
                break
        if print_line:
            print(line)

    def trending_upward(self):
        if len(self.sma_prices) < self.window:
            return False

        upcount = 0

        length = len(self.sma_prices)
        mid = length/2
        #self.compute_linear_regression()
        slope1 = (self.sma_prices[mid] - self.sma_prices[0]) / (mid - 0) #(self.ts[mid] - self.ts[0])
        slope2 = (self.sma_prices[-1] - self.sma_prices[mid]) / (length - mid) #(self.ts[-1] - self.ts[mid])
        slope3 = (self.sma_prices[-1] - self.sma_prices[0]) / (length - 0) #(self.ts[-1] - self.ts[0])

        if slope1 <= 0.0 or slope2 <= 0.0 or slope3 <= 0.0:
            return False


        for i in range(1, len(self.sma_prices)):
            if self.sma_prices[i] >= self.sma_prices[i-1]:
                upcount += 1

        if upcount < int(0.90 * len(self.sma_prices)):
            return False

        #print("trending_upward={} {} {} {}".format(self.name, slope1, slope2, slope3))


        if self.sma_prices[0] == 0.0: return False

        if (self.sma_prices[-1] - self.sma_prices[0]) / self.sma_prices[0] > 0.001:
            return True

        return False

        #if abs(slope1) > 0.1 and abs(slope2) > 0.1 and slope1 > 0.0 and slope2 > 0.0 \
        #    and slope3 > 1.5:
        #    #print(slope1, slope2, slope3)
        #    return True
        #
        #return False

    def trending_downward(self):
        if len(self.sma_prices) < self.window:
            return False

        length = len(self.sma_prices)
        mid = length/2
        #self.compute_linear_regression()
        slope1 = (self.sma_prices[mid] - self.sma_prices[0]) / (mid - 0) #(self.ts[mid] - self.ts[0])
        slope2 = (self.sma_prices[-1] - self.sma_prices[mid]) / (length - mid) #(self.ts[-1] - self.ts[mid])
        slope3 = (self.sma_prices[-1] - self.sma_prices[0]) / (length - 0) #(self.ts[-1] - self.ts[0])

        if slope1 >= 0.0 or slope2 >= 0.0 or slope3 >= 0.0:
            return False

        downcount = 0

        for i in range(1, len(self.sma_prices)):
            if self.sma_prices[i] <= self.sma_prices[i-1]:
                downcount += 1

        if downcount < int(0.8 * len(self.sma_prices)):
            return False


        #if (self.sma_prices[0] - self.sma_prices[-1]) / self.sma_prices[0] > 0.001:
        #    return True
        #print("trending_downward={} {} {} {}".format(self.name, slope1, slope2, slope3))

        return True

        #if abs(slope1) > 0.1 and abs(slope2) > 0.1 and slope1 < 0.0 and slope2 < 0.0 \
        #    and slope3 < -1.0:
        #    #print(slope1, slope2, slope3)
        #    return True
        #return False
