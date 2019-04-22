# use any indicator to process an entire set of data at once, instead of processing it live, and store results

class IndicatorProcess(object):
    def __init__(self, iclass,  *args, **kwargs):
        self.iclass = iclass
        self.indicator = self.iclass(**kwargs)
        self.close_values = None
        self.open_values = None
        self.low_values = None
        self.high_values = None
        self.volume_values = None
        self.ts_values = None
        self.count = 0
        self.results = None
        self.result_count = self.indicator.result_count
        self.close_only = False
        self.close_ts = False
        self.close_volume = False
        self.close_volume_ts = False
        self.close_low_high = False
        self.close_low_high_ts = False
        self.close_low_high_volume = False
        self.close_low_high_volume_ts = False

    # detect type from data available
    def detect_data_type(self):
        if not self.low_values and not self.high_values:
            if self.volume_values:
                if self.ts_values:
                    self.close_volume_ts = True
                else:
                    self.close_volume = True
            else:
                if self.ts_values:
                    self.close_ts = True
                else:
                    self.close_only = True
        else:
            if self.volume_values:
                if self.ts_values:
                    self.close_low_high_volume_ts = True
                else:
                    self.close_low_high_volume = True
            else:
                if self.ts_values:
                    self.close_low_high_ts = True
                else:
                    self.close_low_high = True

    # detect indictator type from IndicatorBase attributes
    def detect_indicator_type(self):
        use_close = self.indicator.use_close
        use_open = self.indicator.use_open
        use_low = self.indicator.use_low
        use_high = self.indicator.use_high
        use_volume = self.indicator.use_volume
        use_ts = self.indicator.use_ts

        if not use_low and not use_high:
            if use_volume:
                if use_ts:
                    self.close_volume_ts = True
                else:
                    self.close_volume = True
            else:
                if use_ts:
                    self.close_ts = True
                else:
                    self.close_only = True
        else:
            if use_volume:
                if use_ts:
                    self.close_low_high_volume_ts = True
                else:
                    self.close_low_high_volume = True
            else:
                if use_ts:
                    self.close_low_high_ts = True
                else:
                    self.close_low_high = True


    # load from pandas dataframe
    def load_dataframe(self, df):
        keys = list(df)
        if 'close' in keys:
            self.close_values = df['close']
        if 'open' in keys:
            self.open_values = df['open']
        if 'low' in keys:
            self.low_values = df['low']
        if 'high' in keys:
            self.high_values = df['high']
        if 'volume' in keys:
            self.close_values = df['volume']
        if 'ts' in keys:
            self.ts_values = df['ts']


    # load list of dict type items
    def load_dict_list(self, data):
        self.count = len(data)
        for d in data:
            if self.indicator.use_close:
                if not self.close_values: self.close_values = []
                self.close_values.append(d['close'])
            if self.indicator.use_ts:
                if not self.ts_values: self.ts_values = []
                self.ts_values.append(d['ts'])
            if self.indicator.use_open:
                if not self.open_values: self.open_values = []
                self.open_values.append(d['open'])
            if self.indicator.use_low:
                if not self.low_values: self.low_values = []
                self.low_values.append(d['low'])
            if self.indicator.use_high:
                if not self.high_values: self.high_values = []
                self.high_values.append(d['high'])
            if self.indicator.use_volume:
                if not self.volume_values: self.volume_values = []
                self.volume_values.append(d['volume'])


    # load list of Kline class items
    def load_kline_list(self, data):
        self.count = len(data)
        for d in data:
            if self.indicator.use_close:
                if not self.close_values: self.close_values = []
                self.close_values.append(d.close)
            if self.indicator.use_ts:
                if not self.ts_values: self.ts_values = []
                self.ts_values.append(d.ts)
            if self.indicator.use_open:
                if not self.open_values: self.open_values = []
                self.open_values.append(d.open)
            if self.indicator.use_low:
                if not self.low_values: self.low_values = []
                self.low_values.append(d.low)
            if self.indicator.use_high:
                if not self.high_values: self.high_values = []
                self.high_values.append(d.high)
            if self.indicator.use_volume:
                if not self.volume_values: self.volume_values = []
                self.volume_values.append(d.volume)


    def process(self):
        self.results = []
        self.detect_indicator_type()
        for i in range(0, self.count):
            close = self.close_values[i]
            if self.close_only:
                self.indicator.update(close)
            elif self.close_ts:
                self.indicator.update(close,
                                      ts=self.ts_values[i])
            elif self.close_volume:
                self.indicator.update(close,
                                      volume=self.volume_values[i])
            elif self.close_volume_ts:
                self.indicator.update(close,
                                      volume=self.volume_values[i],
                                      ts=self.ts_values[i])

            elif self.close_low_high:
                self.indicator.update(close,
                                      low=self.low_values[i],
                                      high=self.high_values[i])
            elif self.close_low_high_ts:
                self.indicator.update(close,
                                      low=self.low_values[i],
                                      high=self.high_values[i],
                                      ts=self.ts_values[i])
            elif self.close_low_high_volume:
                self.indicator.update(close,
                                      low=self.low_values[i],
                                      high=self.high_values[i],
                                      volume=self.volume_values[i])
            elif self.close_low_high_volume_ts:
                self.indicator.update(close,
                                      low=self.low_values[i],
                                      high=self.high_values[i],
                                      volume=self.volume_values[i],
                                      ts=self.ts_values[i])
            else:
                return None
            self.results.append(self.indicator.result)


    def get_results(self):
        if not self.results or not len(self.results):
            self.process()
        return self.results
