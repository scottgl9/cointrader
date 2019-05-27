# Cron tab management
from crontab import CronTab
import getpass


class CronManage(object):
    def __init__(self):
        self.username = getpass.getuser()
        self.cron = CronTab(user=self.username)

    def remove_all_jobs(self):
        for job in self.cron:
            self.cron.remove(job)
        self.cron.write()

    def remove_by_command(self, command):
        for job in self.cron.find_command(command):
            self.cron.remove(job)
        self.cron.write()

    def add_hourly_job(self, cmd, args):
        cmd = "python {} {}".format(cmd, args)
        job = self.cron.new(command=cmd)
        # run at the very beginning of each hour
        job.every(1).hours()
        self.cron.write()
