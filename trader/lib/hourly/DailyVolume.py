# hourly indicator for 24 hour (daily) volume


class DailyVolume(object):
    def __init__(self, window=24):
        self.window = window
        self.volumes = []
        self.age = 0
        self._volume_sum = 0
        self.result = 0

    def ready(self):
        return len(self.volumes) == self.window

    def update(self, volume):
        if len(self.volumes) < self.window:
            self._volume_sum += volume
            self.volumes.append(volume)
        else:
            self._volume_sum -= self.volumes[int(self.age)]
            self._volume_sum += volume
            self.volumes[int(self.age)] = volume
            self.age = (self.age + 1) % self.window
            self.result = self._volume_sum
        return self.result
