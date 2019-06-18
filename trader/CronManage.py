# Cron tab management
from crontab import CronTab
import getpass


class CronManage(object):
    def __init__(self):
        self.username = getpass.getuser()
        self.cron = None

    def remove_all_jobs(self):
        for job in self.cron:
            self.cron.remove(job)
        self.cron.write()

    def remove_by_command(self, command):
        for job in self.cron.find_command(command):
            self.cron.remove(job)
        self.cron.write()

    def add_hourly_job(self, cmd, args):
        tab = "0 */1 * * * python {} {}".format(cmd, args)
        self.cron = CronTab(user=self.username, tab=tab)
        # run at the very beginning of each hour
        #job.every(1).hours()
        self.cron.write()
