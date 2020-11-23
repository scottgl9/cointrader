class FeedSync(object):
    def __init__(self, init_ts=0):
        self.init_ts = init_ts
        self.ts = init_ts

    def update_ts(self, ts):
        self.ts = ts

    def get_ts(self):
        return self.ts
