from trader.lib.MovingTimeSegment.MovingTimeSegment import MovingTimeSegment


class MTSVolumeSum(object):
    def __init__(self, seconds=3600):
        self.seconds = seconds
        self.mts = MovingTimeSegment(seconds=self.seconds)
        self.result = 0

    def ready(self):
        return self.mts.ready()

    def update(self, volume, ts):
        self.mts.update(volume, ts)
        self.result = self.mts.get_sum()
        return self.result
