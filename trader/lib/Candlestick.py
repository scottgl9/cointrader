# Library for finding candlestick patterns

class Candlestick(object):
    def __init__(self):
        self.prev_kline = None

    def update(self, kline):

        self.prev_kline = kline

    @staticmethod
    def body_length(kline):
        return abs(kline.open - kline.close)

    @staticmethod
    def wick_length(kline):
        return kline.high - max(kline.open, kline.close)

    @staticmethod
    def tail_length(kline):
        return min(kline.open, kline.close) - kline.low

    @staticmethod
    def is_bullish(kline):
        return kline.open < kline.close

    @staticmethod
    def is_bearish(kline):
        return kline.open > kline.close

    @staticmethod
    def is_hammer_like(kline):
        return (Candlestick.tail_length(kline) > (Candlestick.body_length(kline) * 2) and
               Candlestick.wick_length(kline) < Candlestick.body_length(kline))

    @staticmethod
    def is_inverted_hammer_like(kline):
        return (Candlestick.wick_length(kline) > (Candlestick.body_length(kline) * 2) and
               Candlestick.tail_length(kline) < Candlestick.body_length(kline))

    @staticmethod
    def is_engulfed(shortest, longest):
        return Candlestick.body_length(shortest) < Candlestick.body_length(longest)

    @staticmethod
    def is_gap(lowest, upmost):
        return max(lowest.open, lowest.close) < min(upmost.open, upmost.close)

    @staticmethod
    def is_gap_up(previous, current):
        return Candlestick.is_gap(previous, current)

    @staticmethod
    def is_gap_down(previous, current):
        return Candlestick.is_gap(current, previous)

    # Boolean pattern detection.

    @staticmethod
    def is_marubozu(kline):
        if kline.close == kline.high and kline.open == kline.low:
            return True
        if kline.open == kline.high and kline.close == kline.low:
            return True
        return False

    @staticmethod
    def is_spinning_top(kline):
        body_len = Candlestick.body_length(kline)
        return body_len < Candlestick.wick_length(kline) and body_len < Candlestick.tail_length(kline)

    @staticmethod
    def is_hammer(kline):
        return Candlestick.is_bullish(kline) and Candlestick.is_hammer_like(kline)

    @staticmethod
    def is_inverted_hammer(kline):
        return Candlestick.is_bearish(kline) and Candlestick.is_inverted_hammer_like(kline)

    @staticmethod
    def is_marubozu_bullish(kline):
        return Candlestick.is_bullish(kline) and Candlestick.is_marubozu(kline)

    @staticmethod
    def is_marubozu_bearish(kline):
        return Candlestick.is_bearish(kline) and Candlestick.is_marubozu(kline)

    @staticmethod
    def is_spinning_top_bullish(kline):
        return Candlestick.is_bullish(kline) and Candlestick.is_spinning_top(kline)

    @staticmethod
    def is_spinning_top_bearish(kline):
        return Candlestick.is_bearish(kline) and Candlestick.is_spinning_top(kline)

    @staticmethod
    def is_hanging_man(previous, current):
        return (Candlestick.is_bullish(previous) and
               Candlestick.is_bearish(current) and
               Candlestick.is_gap_up(previous, current) and
               Candlestick.is_hammer_like(current))

    @staticmethod
    def is_shooting_star(previous, current):
        return (Candlestick.is_bullish(previous) and
               Candlestick.is_bearish(current) and
               Candlestick.is_gap_up(previous, current) and
               Candlestick.is_inverted_hammer_like(current))

    @staticmethod
    def is_bullish_engulfing(previous, current):
        return (Candlestick.is_bearish(previous) and
               Candlestick.is_bullish(current) and
               Candlestick.is_engulfed(previous, current))

    @staticmethod
    def is_bearish_engulfing(previous, current):
        return (Candlestick.is_bullish(previous) and
               Candlestick.is_bearish(current) and
               Candlestick.is_engulfed(previous, current))

    @staticmethod
    def is_bullish_harami(previous, current):
        return (Candlestick.is_bearish(previous) and
               Candlestick.is_bullish(current) and
               Candlestick.is_engulfed(current, previous))

    @staticmethod
    def is_bearish_harami(previous, current):
        return (Candlestick.is_bullish(previous) and
               Candlestick.is_bearish(current) and
               Candlestick.is_engulfed(current, previous))

    @staticmethod
    def is_bullish_kicker(previous, current):
        return (Candlestick.is_bearish(previous) and
               Candlestick.is_bullish(current) and
               Candlestick.is_gap_up(previous, current))

    @staticmethod
    def is_bearish_kicker(previous, current):
        return (Candlestick.is_bullish(previous) and
               Candlestick.is_bearish(current) and
               Candlestick.is_gap_down(previous, current))
