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
        self.cur_id = 1
        self.buy_signal_id = 0
        self.sell_signal_id = 0

    def empty(self):
        return len(self.handlers) == 0

    def add(self, handler):
        handler.set_id(self.cur_id)
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

    def get_handler(self, id):
        for handler in self.handlers:
            if handler.id == id:
                return handler
        return None

    def get_buy_signal_id(self, clear=True):
        id = self.buy_signal_id
        if clear:
            self.buy_signal_id = 0
        return id

    def get_sell_signal_id(self, clear=True):
        id = self.sell_signal_id
        if clear:
            self.sell_signal_id = 0
        return id

    def get_handler_signaled(self, clear=True):
        handler = self.last_handler_signaled
        if clear:
            self.clear_handler_signaled()
        return handler

    def clear_handler_signaled(self):
        self.last_handler_signaled = None

    def buy_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.get_handlers():
            if handler.buy_signal():
                if self.sigtype == self.SIGNAL_ONE:
                    self.buy_type = handler.buy_type
                    self.last_handler_signaled = handler
                    self.buy_signal_id = handler.id
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
                self.sell_signal_id = handler.id
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
                    self.sell_signal_id = handler.id
                    return True
            elif self.sigtype == self.SIGNAL_ALL:
                return False

        if self.sigtype == self.SIGNAL_ALL:
            return True

        return False
