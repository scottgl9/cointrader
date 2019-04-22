class IndicatorBase:
    def __init__(self, use_close=True, use_open=False, use_volume=False, use_low=False, use_high=False, use_ts=False,
                 result_count=1):
        self.use_close = use_close
        self.use_open = use_open
        self.use_volume = use_volume
        self.use_low = use_low
        self.use_high = use_high
        self.use_ts = use_ts
        self.result_count = result_count
        self.close_only = False
        self.close_ts = False
        self.close_volume = False
        self.close_volume_ts = False
        self.close_low_high = False
        self.close_low_high_ts = False
        self.close_low_high_volume = False
        self.close_low_high_volume_ts = False

    # detect indictator type from use attributes
    def detect_type(self):
        if not self.use_low and not self.use_high:
            if self.use_volume:
                if self.use_ts:
                    self.close_volume_ts = True
                else:
                    self.close_volume = True
            else:
                if self.use_ts:
                    self.close_ts = True
                else:
                    self.close_only = True
        else:
            if self.use_volume:
                if self.use_ts:
                    self.close_low_high_volume_ts = True
                else:
                    self.close_low_high_volume = True
            else:
                if self.use_ts:
                    self.close_low_high_ts = True
                else:
                    self.close_low_high = True
