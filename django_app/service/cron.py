from datetime import datetime
from .models import Schedule as ScheduleModel
from django_cron import CronJobBase, Schedule
import pytz

utc = pytz.UTC


class SetStatusJob(CronJobBase):
    """
    Set current massage status
    """
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "service.cron.SetStatusJob"

    def do(self):
        print(1)
