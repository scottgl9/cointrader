# hourly update handler to update hourly klines DB
import time
import threading
from queue import Queue
from trader.HourlyKlinesDB import HourlyKlinesDB


class HourlyUpdateHandler(threading.Thread):
    def __init__(self, accnt, hourly_klines_db_file, logger):
        threading.Thread.__init__(self)
        self.accnt = accnt
        self.hourly_klines_db_file = hourly_klines_db_file
        self.logger = logger
        self.start_ts = int(time.time())
        self.start_hourly_ts = int(time.time() / 3600) * 3600
        self.last_hourly_ts = self.start_hourly_ts
        self.info = HourlyUpdateInfo()
        self.info.last_hourly_update_ts = self.last_hourly_ts
        self.hkdb = None
        self._running = False
        self.daemon = True

    def ready(self):
        return self.info.last_hourly_update_ts != 0

    def get_last_hourly_update_ts(self):
        return self.info.last_hourly_update_ts

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        self.hkdb = HourlyKlinesDB(self.accnt, self.hourly_klines_db_file, self.logger)
        #hourly_start_ts = int(self.start_ts / 3600) * 3600
        #last_hourly_ts = hourly_start_ts
        self.logger.info("HourlyUpdateHandler started on {}".format(time.ctime(int(time.time()))))

        while self._running:
            if (int(time.time()) - self.last_hourly_ts) >= 3600:
                # wait 15 seconds before updating tables
                time.sleep(15)
                self.logger.info("Updating hourly DB tables on {}".format(time.ctime(int(time.time()))))
                self.hkdb.update_all_tables()
                self.last_hourly_ts = int(time.time() / 3600) * 3600
                self.info.last_hourly_update_ts = self.last_hourly_ts
            time.sleep(1)
        self.hkdb.close()

class HourlyUpdateInfo(object):
    def __init__(self):
        self.last_hourly_update_ts = 0
