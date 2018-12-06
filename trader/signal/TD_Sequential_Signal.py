# TD Sequential Indicator / Signal
from trader.lib.CircularArray import CircularArray
from trader.lib.FakeKline import FakeKline
from trader.lib.PriceFilter import PriceFilter
from trader.signal.SignalBase import SignalBase

class TD_Sequential_Signal(SignalBase):
    def __init__(self, accnt=None, window=13, close_count=9):
        super(TD_Sequential_Signal, self).__init__(accnt)
        self.signal_name = "TD_Sequential_Signal"
        self.close_prices = CircularArray(window=window)
        self.low_prices = CircularArray(window=window)
        self.high_prices = CircularArray(window=window)
        self.fkline = FakeKline()
        self.window = window
        self.close_count = close_count
        self.last_age = 0
        self.age = 0
        self.filter = PriceFilter()

        self.bearish_flip = False
        self.bullish_flip = False
        # buy setup vars
        self.isBuySetup = False
        self.buyCountdownCompleted = False
        self.bSetupCounter = 0
        self.bCountDownCounter = 0

        self.isSellSetup = False
        self.sellCountdownCompleted = False
        self.sSetupCounter = 0
        self.sCountDownCounter = 0

    # You count only the bars that close higher (lower) or equal to the high (low) of Sell (Buy) Countdown close 2 bars earlier.
    def get_next_countdown(self):
        if self.isBuySetup:
            close = self.close_prices.last()
            low = self.low_prices.get_value(-3)
            if close <= low:
                self.bCountDownCounter += 1

        if self.isSellSetup:
            close = self.close_prices.last()
            high = self.high_prices.get_value(-3)
            if close >= high:
                self.sCountDownCounter += 1

        if self.bCountDownCounter == self.window:
            low13 = self.low_prices.last()
            close8 = self.close_prices.get_value(-6)
            close13 = self.close_prices.last()
            low8 = self.low_prices.get_value(-6)
            if low13 <= close8:
                self.buyCountdownCompleted = True
            self.bCountDownCounter = 0

        if self.sCountDownCounter == self.window:
            high13 = self.high_prices.last()
            close8 = self.close_prices.get_value(-6)
            close13 = self.close_prices.last()
            high8 = self.high_prices.get_value(-6)
            if high13 >= close8: # and close13 >= high8:
                self.sellCountdownCompleted = True
            self.sCountDownCounter = 0

    def get_next_setup(self):
        if not self.close_prices.full():
            return
        close1 = self.close_prices.last()
        close5 = self.close_prices.get_value(-5)
        if close1 < close5:
            self.bSetupCounter += 1
            self.sSetupCounter = 0
        elif close1 > close5:
            self.bSetupCounter = 0
            self.sSetupCounter += 1

        if self.isBuySetup and self.sSetupCounter == self.close_count:
            self.isBuySetup = False
            self.bCountDownCounter = 0
            return

        if self.isSellSetup and self.bSetupCounter == self.close_count:
            self.isSellSetup = False
            self.sCountDownCounter = 0
            return

        if self.bSetupCounter == self.close_count and self.sSetupCounter == 0:
            low9 = self.low_prices.get_value(-1)
            low8 = self.low_prices.get_value(-2)
            low7 = self.low_prices.get_value(-3)
            low6 = self.low_prices.get_value(-4)
            if low9 <= low6 and low9 <= low7:
                self.isBuySetup = True
            if low8 <= low6 and low8 <= low7:
                self.isBuySetup = True
            self.bSetupCounter = 0

        if self.sSetupCounter == self.close_count and self.bSetupCounter == 0:
            high9 = self.high_prices.get_value(-1)
            high8 = self.high_prices.get_value(-2)
            high7 = self.high_prices.get_value(-3)
            high6 = self.high_prices.get_value(-4)
            if high9 >= high6 and high9 >= high7:
                self.isSellSetup = True
            if high8 >= high6 and high8 >= high7:
                self.isSellSetup = True
            self.sSetupCounter = 0

    def pre_update(self, close, volume=0, ts=0):
        if close in self.fkline.values.carray:
            return
        close = self.filter.update(close)
        if close == 0:
            return
        open, close, low, high, volume = self.fkline.update(close=close, volume=volume)
        self.close_prices.add(float(close))
        self.low_prices.add(float(low))
        self.high_prices.add(float(high))
        self.get_next_setup()
        self.get_next_countdown()

    def post_update(self):
        pass

    #  the low of bars 8 or 9 should be lower or equal to the low of bar 6 and bar 7 in Buy Setup.
    def buy_signal(self):
        if self.buyCountdownCompleted:
            self.buyCountdownCompleted = False
            self.isBuySetup = False
            self.bullish_flip = False
            self.bCountDownCounter = 0
            self.bCountDownCounter = 0
            return True
        return False

    #  the high of bars 8 or 9 should be higher or equal to the high of bar 6 and bar 7 in Sell Setup.
    def sell_signal(self):
        if self.sellCountdownCompleted:
            self.sellCountdownCompleted= False
            self.isSellSetup = False
            self.bearish_flip = False
            self.sCountDownCounter = 0
            self.sSetupCounter = 0
            return True
        return False
