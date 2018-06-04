# TD Sequential Indicator / Signal
from trader.lib.CircularArray import CircularArray
from trader.lib.FakeKline import FakeKline

class TD_Sequential_Signal(object):
    def __init__(self, window=13):
        self.close_prices = CircularArray(window=window)
        self.low_prices = CircularArray(window=window)
        self.high_prices = CircularArray(window=window)
        self.fkline = FakeKline()
        self.window = window
        self.last_age = 0
        self.age = 0

        self.bearish_flip = False
        self.bullish_flip = False
        # buy setup vars
        self.isBuySetup = False
        self.isBuyCountDownStarted = False
        self.bSetupCounter = 0
        self.bCountDownCounter = 0

        self.isSellSetup = False
        self.isSellCountDownStarted = False
        self.sSetupCounter = 0
        self.sCountDownCounter = 0

    def get_next_countdown(self):
        pass

    def get_next_setup(self):
        close1 = self.close_prices.get_value(-1)
        close5 = self.close_prices.get_value(-5)
        if close1 < close5:
            self.bSetupCounter += 1
            self.sSetupCounter = 0
        elif close1 > close5:
            self.bSetupCounter = 0
            self.sSetupCounter += 1

    def pre_update(self, close, volume, ts):
        open, close, low, high, volume = self.fkline.update(close=close, volume=volume)
        self.close_prices.add(float(close))
        self.low_prices.add(float(low))
        self.high_prices.add(float(high))
        self.get_next_setup()

    def post_update(self):
        pass

    def buy_signal(self):
        if self.sSetupCounter > 0:
            return False
        if self.bSetupCounter >= 9:
            return True
        return False

    def sell_signal(self):
        if self.bSetupCounter > 0:
            return False
        if self.sSetupCounter >= 9:
            return True
        return False
