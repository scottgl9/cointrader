#import collections


class Kline(object):
    def __init__(self, symbol=None, open=0, close=0, low=0, high=0,
                 volume_base=0, volume_quote=0, ts=0):
        self.symbol = symbol
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume_base = volume_base
        self.volume_quote = volume_quote
        self.volume = volume_quote
        self.ts = ts

    def __repr__(self):
        return {
            'open': float(self.open),
            'close': float(self.close),
            'volume_base': float(self.volume_base),
            'volume_quote': float(self.volume_quote),
            'ts': int(self.ts)
        }

    def reset(self):
        self.symbol = None
        self.open = 0
        self.close = 0
        self.low = 0
        self.high = 0
        self.volume_base = 0
        self.volume_quote = 0
        self.volume = 0
        self.ts = 0

# class KlineList(collections.MutableSequence):
#     def __init__(self, *args):
#         self.oktypes = Kline
#         self.list = list()
#         self.extend(list(args))
#
#     def check(self, v):
#         if not isinstance(v, self.oktypes):
#             raise TypeError, v
#
#     def __len__(self): return len(self.list)
#
#     def __getitem__(self, i): return self.list[i]
#
#     def __delitem__(self, i): del self.list[i]
#
#     def __setitem__(self, i, v):
#         self.check(v)
#         self.list[i] = v
#
#     def insert(self, i, v):
#         self.check(v)
#         self.list.insert(i, v)
#
#     def __str__(self):
#         return str(self.list)
