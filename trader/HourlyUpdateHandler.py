# hourly update handler to update hourly klines DB
import time
import threading
from queue import Queue
from trader.HourlyKlinesDB import HourlyKlinesDB


class HourlyUpdateHandler(object):
    def __init__(self, accnt, hourly_klines_db_file, logger):
        self.start_ts = int(time.time())
        self._last_hourly_update_ts = 0
        self.info = HourlyUpdateInfo()
        self.t = threading.Thread(target=self.run,
                                  args=(self.start_ts, self.info, accnt, hourly_klines_db_file, logger,))
        self.t.daemon = True
        self.t.start()

    def join(self):
        self.t.join()

    def ready(self):
        return self._last_hourly_update_ts != 0

    # get last hourly_ts of a successful update of all hourly DB tables
    def last_hourly_update_ts(self):
        if not self.info.last_hourly_update_ts:
            return self._last_hourly_update_ts
        self._last_hourly_update_ts = self.info.last_hourly_update_ts
        return self._last_hourly_update_ts * 1000

    def run(self, start_ts, info, accnt, hourly_klines_db_file, logger):
        hkdb = HourlyKlinesDB(accnt, hourly_klines_db_file, logger)
        hourly_start_ts = int(start_ts / 3600) * 3600
        last_hourly_ts = hourly_start_ts
        logger.info("HourlyUpdateHandler started on {}".format(time.ctime(int(time.time()))))

        while True:
            if (int(time.time()) - last_hourly_ts) >= 3600:
                time.sleep(1)
                logger.info("Updating hourly DB tables on {}".format(time.ctime(int(time.time()))))
                hkdb.update_all_tables()
                last_hourly_ts = int(time.time() / 3600) * 3600
                info.last_hourly_update_ts = last_hourly_ts
            time.sleep(1)

class HourlyUpdateInfo(object):
    def __init(self):
        self.last_hourly_update_ts = 0
