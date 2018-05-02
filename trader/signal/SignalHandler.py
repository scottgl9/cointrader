

class SignalHandler(object):
    def __init__(self):
        self.handlers = []

    def add(self, handler):
        self.handlers.append(handler)

    def remove(self, handler):
        self.handlers.remove(handler)

    def pre_update(self, close, volume):
        if len(self.handlers) == 0:
            return

        for handler in self.handlers:
            handler.pre_update(close=close, volume=volume)

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
                return True

        return False

    def sell_signal(self):
        if len(self.handlers) == 0:
            return False

        for handler in self.handlers:
            if handler.sell_signal():
                return True

        return False
