import time
import threading


class FeedBase(threading.Thread):
    def __init__(self, mt, sync, refresh_secs=0, use_db=False, db_filename="", feed_type=1, live=True):
        threading.Thread.__init__(self)

        # MultiTrader
        self.mt = mt
        # FeedSync
        self.sync = sync
        # 0 indicates realtime feed, other value is refresh rate in secs
        self.refresh_secs = refresh_secs
        self.use_db = use_db
        self.db_filename = db_filename
        self.feed_type = feed_type
        self.live = live

        self.feed_no = 1
        self.db = None
        self._running = False
        self.daemon = True

    def stop(self):
        self._running = False

    def run(self):
        self._running = True

        while self._running:
            self.run_feed()

    # override function
    def run_feed(self):
        time.sleep(1)

    def set_feed_number(self, n):
        self.feed_no = n

    def get_feed_number(self):
        return self.feed_no

    def close(self):
        if self.db:
            self.db.close()
