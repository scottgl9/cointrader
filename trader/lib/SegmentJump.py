# need to come up with a better name, detect substantial change in movement upward or downward
from trader.lib.TimeSegmentValues import TimeSegmentValues


class SegmentJump(object):
    def __init__(self, multiplier=2):
        self.tsv1 = TimeSegmentValues(minutes=5)
        self.tsv2_up = TimeSegmentValues(minutes=30)
        self.tsv2_down = TimeSegmentValues(minutes=30)
        self.tsv1_ready = False
        self.tsv2_up_ready = False
        self.tsv2_down_ready = False
        self.multiplier = multiplier
        self.up = False
        self.down = False
        self.last_up = False
        self.last_down = False

    def update(self, value, ts):
        self.tsv1.update(value, ts)

        if not self.tsv1_ready:
            if self.tsv1.ready():
                self.tsv1_ready = True
            else:
                return 0

        diff = self.tsv1.diff()
        if diff > 0:
            self.tsv2_up.update(diff, ts)
        elif diff < 0:
            self.tsv2_down.update(abs(diff), ts)

        result = diff

        if not self.tsv2_up_ready:
            if self.tsv2_up.ready():
                self.tsv2_up_ready = True

        if not self.tsv2_down_ready:
            if self.tsv2_down.ready():
                self.tsv2_down_ready = True

        if self.tsv2_up_ready and self.tsv1.values[-1] > 0:
            # check for 'jump' in uptrend
            if self.tsv1.values[-1] > self.tsv2_up.min() * self.multiplier:
                self.up = True
                self.down = False
        elif self.tsv2_down_ready and self.tsv1.values[-1] < 0:
            # check for 'jump in downtrend'
            if abs(self.tsv1.values[-1]) > self.tsv2_up.min() * self.multiplier:
                self.up = False
                self.down = True

        return result

    def up_detected(self, clear=True):
        result = False
        if self.up:
            result = True
        if clear:
            self.up = False
        return result

    def down_detected(self, clear=True):
        result = False
        if self.down:
            result = True
        if clear:
            self.down = False
        return result
