"""
Scheduler utilities for Nexora.

This module configures APScheduler jobs based on the enabled
automations for each client.  It is invoked by the application
factory during start‑up.
"""

from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from ..models import AutomationInstance
from .automations import run_follow_up_sequence, run_daily_digest


def schedule_jobs(scheduler: BackgroundScheduler) -> None:
    """Iterate over enabled automation instances and schedule appropriate jobs.

    Only automations that require periodic execution (follow‑up sequence
    and daily digest) are scheduled.  Trigger‑based automations are
    invoked from within the application when relevant events occur.
    """
    # Remove existing jobs to avoid duplicates
    for job in scheduler.get_jobs():
        scheduler.remove_job(job.id)

    instances = AutomationInstance.query.filter_by(enabled=True).all()
    for ai in instances:
        if ai.template.type == "follow_up_sequence":
            job_id = f"follow_up_{ai.client_id}_{ai.id}"
            # Run daily at 00:30 UTC
            scheduler.add_job(
                run_follow_up_sequence,
                trigger=CronTrigger(hour=0, minute=30),
                args=[ai],
                id=job_id,
                replace_existing=True,
            )
        elif ai.template.type == "daily_digest":
            job_id = f"daily_digest_{ai.client_id}_{ai.id}"
            # Run daily at 01:00 UTC
            scheduler.add_job(
                run_daily_digest,
                trigger=CronTrigger(hour=1, minute=0),
                args=[ai],
                id=job_id,
                replace_existing=True,
            )