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
        self.result_count = self.indicator.result_count
        self.close_only = False
        self.close_ts = False
        self.close_volume = False
        self.close_volume_ts = False
        self.close_low_high = False
        self.close_low_high_ts = False
        self.close_low_high_volume = False
        self.close_low_high_volume_ts = False

    def detect_type(self):
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
        self.detect_type()
        for i in range(0, self.count):
            pass


    def get_results(self):
        pass
