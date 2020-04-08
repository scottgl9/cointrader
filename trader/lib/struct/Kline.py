# Kline (OHLCV) class


class Kline(object):
    def __init__(self, symbol=None, open=0, close=0, low=0, high=0,
                 volume=0, ts=0, exchange_type=0):
        self.symbol = symbol
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume
        self.ts = ts
        self.exchange_type = exchange_type

    def __repr__(self):
        return {
            'symbol': self.symbol,
            'open': float(self.open),
            'close': float(self.close),
            'low': float(self.low),
            'high': float(self.high),
            'volume': float(self.volume),
            'ts': int(self.ts),
            'exchange_type': int(self.exchange_type)
        }

    def __str__(self):
        return str(self.__repr__())

    def reset(self):
        self.symbol = None
        self.open = 0
        self.close = 0
        self.low = 0
        self.high = 0
        self.volume = 0
        self.ts = 0
        self.exchange_type = 0
