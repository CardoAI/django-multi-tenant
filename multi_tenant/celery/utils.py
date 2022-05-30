import json
import logging

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from applications.multi_tenant.db import DatabaseAlias

logger = logging.getLogger(__name__)


def from_schedule_to_database(schedule, database_alias):
    """
    Takes a CELERY_BEAT_SCHEDULE and converts it to
    CrontabSchedule and PeriodicTask records.
    The schedule is a dictionary with the following structure:
    {
        'task': 'applications.multi_tenant.tasks.task_name',
        'schedule': crontab(minute='*/5'),
        'args': (arg1, arg2),
        'kwargs': {'key': 'value'},
        'options': {'queue': 'queue_name'},
        'id': 'task_name'
    }
    """
    DatabaseAlias.set(database_alias)

    for name, s in schedule.items():
        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=s['schedule']._orig_minute,
            hour=s['schedule']._orig_hour,
            day_of_week=s['schedule']._orig_day_of_week,
            day_of_month=s['schedule']._orig_day_of_month,
            month_of_year=s['schedule']._orig_month_of_year,
        )
        PeriodicTask.objects.create(
            crontab=crontab_schedule,
            name=name,
            task=s['task'],
            kwargs=json.dumps(s['kwargs'])
        )
