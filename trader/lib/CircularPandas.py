import numpy as np
import pandas as pd
from trader.lib.CircularArray import CircularArray

class CircularPandas(object):
    def __init__(self, window):
        self.window = window
        self.array = CircularArray(window=window)
        self.last_age = 0
        self.age = 0
        self.df = pd.DataFrame(columns=['close', 'volume', 'ts'])

    def ready(self):
        return not self.df.empty

    def get_data_frame(self):
        return self.df

    def update(self, close, volume, ts):
        self.array.add((close, volume, ts))

        if len(self.array) < self.window:
            return
            #self.df = pd.DataFrame.from_records(self.array.values(), columns=['close', 'volume', 'ts'])
        else:
            self.df = pd.DataFrame.from_records(self.array.values_ordered(), columns=['close', 'volume', 'ts'])
        #if self.df.empty:
        #    self.carray.append((close, volume, ts))
        #    # create initial pandas DataFrame
        #    self.df = pd.DataFrame.from_records(self.carray, columns=['close', 'volume', 'ts'])
        #    return

        #self.df.loc[self.age, :] = (close, volume, ts)

        self.last_age = self.age
        self.age = (self.age + 1) % self.window
        return
