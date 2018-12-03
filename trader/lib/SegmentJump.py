# need to come up with a better name, detect substantial change in movement upward or downward
from trader.lib.TimeSegmentValues import TimeSegmentValues


class SegmentJump(object):
    def __init__(self, tsv1_minutes=5, tsv2_minutes=30, up_multiplier=2, down_multiplier=2, filter=None):
        self.tsv1_minutes = tsv1_minutes
        self.tsv2_minutes = tsv2_minutes
        self.tsv1 = TimeSegmentValues(minutes=tsv1_minutes)
        self.tsv2_up = TimeSegmentValues(minutes=tsv2_minutes)
        self.tsv2_down = TimeSegmentValues(minutes=tsv2_minutes)
        self.tsv1_ready = False
        self.tsv2_up_ready = False
        self.tsv2_down_ready = False
        self.up_multiplier = up_multiplier
        self.down_multiplier = down_multiplier
        self.filter = filter
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

        if self.filter:
            diff = self.filter.update(self.tsv1.diff())
        else:
            diff = self.tsv1.diff()

        if not self.tsv2_up_ready:
            if self.tsv2_up.ready():
                self.tsv2_up_ready = True

        if not self.tsv2_down_ready:
            if self.tsv2_down.ready():
                self.tsv2_down_ready = True

        if self.tsv2_up_ready and diff > 0:
            # check for 'jump' in uptrend
            if diff > self.tsv2_up.max() * self.up_multiplier: # and diff > self.tsv2_down.max() * self.multiplier:
                self.up = True
                self.down = False
        elif self.tsv2_down_ready and diff < 0:
            # check for 'jump in downtrend'
            if abs(diff) > self.tsv2_down.max() * self.down_multiplier:
                self.up = False
                self.down = True

        if diff > 0:
            self.tsv2_up.update(diff, ts)
        elif diff < 0:
            self.tsv2_down.update(abs(diff), ts)

        result = diff

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
