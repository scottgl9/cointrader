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
