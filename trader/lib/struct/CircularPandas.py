import pandas as pd
from trader.lib.struct.CircularArray import CircularArray

class CircularPandas(object):
    def __init__(self, window):
        self.window = window
        self.closes = CircularArray(window=window)
        self.volumes = CircularArray(window=window)
        self.timestamps = CircularArray(window=window)
        self.last_age = 0
        self.age = 0
        self.df = pd.DataFrame(columns=['close', 'volume', 'ts'])

    def ready(self):
        return not self.df.empty

    def get_data_frame(self):
        return self.df

    def update(self, kline):
        self.closes.add(kline.close)
        self.volumes.add(kline.volume)
        self.timestamps.add(kline.ts)

        if len(self.closes) < self.window:
            return
            #self.df = pd.DataFrame.from_records(self.array.values(), columns=['close', 'volume', 'ts'])
        elif self.df.empty:
            self.df = pd.DataFrame.from_dict({'close':self.closes.values_ordered(),
                                              'volume':self.volumes.values_ordered(),
                                              'timestamp':self.timestamps.values_ordered()})

        #if self.df.empty:
        #    self.carray.append((close, volume, ts))
        #    # create initial pandas DataFrame
        #    self.df = pd.DataFrame.from_records(self.carray, columns=['close', 'volume', 'ts'])
        #    return

        #self.df.loc[self.age, :] = (close, volume, ts)

        self.last_age = self.age
        self.age = (self.age + 1) % self.window
        return
