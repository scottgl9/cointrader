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
        self.last_handler_signaled = None
        self.last_handler_buy_signaled = None
        self.last_handler_sell_signaled = None
        self.cur_id = 1

    def empty(self):
        return len(self.handlers) == 0

    def add(self, handler):
        self.cur_id += 1
        self.handlers.append(handler)

    def remove(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)

    def pre_update(self, close, volume, ts=0):
        if self.empty():
            return

        for handler in self.handlers:
            handler.pre_update(close=close, volume=volume, ts=ts)

    def post_update(self, close, volume):
        if self.empty():
            return

        for handler in self.handlers:
            handler.post_update(close=close, volume=volume)

    def get_handlers(self):
        return self.handlers

    def get_handler_signaled(self, clear=True):
        handler = self.last_handler_signaled
        if clear:
            self.last_handler_signaled = None
        return handler

    def buy_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.get_handlers():
            if handler.buy_signal():
                if self.sigtype == self.SIGNAL_ONE:
                    self.buy_type = handler.buy_type
                    self.last_handler_signaled = handler
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
                self.last_handler_signaled = handler
                return True

        return False

    def sell_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.get_handlers():
            if handler.sell_signal():
                if self.sigtype == self.SIGNAL_ONE:
                    self.buy_type = handler.buy_type
                    self.sell_type = handler.sell_type
                    self.last_handler_signaled = handler
                    return True
            elif self.sigtype == self.SIGNAL_ALL:
                return False

        if self.sigtype == self.SIGNAL_ALL:
            return True

        return False
