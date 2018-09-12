from trader.signal.SigType import SigType


class SignalHandler(object):
    SIGNAL_ONE = 1
    SIGNAL_ALL = 2

    def __init__(self, sigtype=SIGNAL_ONE, logger=None):
        self.handlers = []
        self.sigtype = sigtype
        self.logger = logger
        self.buy_type = SigType.SIGNAL_NONE
        self.sell_type = SigType.SIGNAL_NONE

    def add(self, handler):
        self.handlers.append(handler)

    def remove(self, handler):
        self.handlers.remove(handler)

    def pre_update(self, close, volume, ts=0):
        if len(self.handlers) == 0:
            return

        for handler in self.handlers:
            handler.pre_update(close=close, volume=volume, ts=ts)

    def post_update(self, close, volume):
        if len(self.handlers) == 0:
            return

        for handler in self.handlers:
            handler.post_update(close=close, volume=volume)

    def buy_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.handlers:
            if handler.buy_signal():
                if self.sigtype == self.SIGNAL_ONE:
                    self.buy_type = handler.buy_type
                    return True
            elif self.sigtype == self.SIGNAL_ALL:
                return False

        if self.sigtype == self.SIGNAL_ALL:
            return True

        return False

    def sell_long_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.handlers:
            if handler.sell_long_signal():
                return True

        return False

    def sell_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.handlers:
            if handler.sell_signal():
                if self.sigtype == self.SIGNAL_ONE:
                    self.buy_type = handler.buy_type
                    self.sell_type = handler.sell_type
                    return True
            elif self.sigtype == self.SIGNAL_ALL:
                return False

        if self.sigtype == self.SIGNAL_ALL:
            return True

        return False
