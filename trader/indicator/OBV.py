
class OBV(object):
    def __init__(self):
        self.result = 0.0
        self.last_result = 0.0
        self.last_close = 0.0

    def update(self, close, volume):
        self.last_result = self.result
        if self.result == 0:
            self.result = float(volume)
            self.last_close = close
            return self.result

        if close > self.last_close:
            self.result += float(volume)
        elif close < self.last_close:
            self.result -= float(volume)

        self.last_close = close

        return self.result

