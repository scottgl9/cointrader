# hourly indicator for 24 hour (daily) volume


class DailyVolume(object):
    def __init__(self, window=24):
        self.window = window
        self.volumes = []
        self.age = 0
        self._volume_sum = 0
        self.last_ts = 0
        self.result = 0

    def ready(self):
        return len(self.volumes) == self.window

    def update(self, volume, ts=0):
        if len(self.volumes) < self.window:
            self._volume_sum += volume
            self.volumes.append(volume)
        else:
            self._volume_sum -= self.volumes[int(self.age)]
            self._volume_sum += volume
            self.volumes[int(self.age)] = volume
            self.age = (self.age + 1) % self.window
            self.result = self._volume_sum

        self.last_ts = ts

        return self.result
