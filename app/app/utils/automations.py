"""
Automation handlers for Nexora V1.

Each function corresponds to an automation template.  They perform
actions (e.g. sending emails, updating records) and log results via
`LogEntry`.  Real integrations (e.g. Google Workspace) can be added by
expanding these functions.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from flask import current_app

from .. import db
from ..models import (
    AutomationInstance,
    Lead,
    Job,
    LogEntry,
    User,
)
from .email import send_email


def _log(client_id: int, automation_instance_id: Optional[int], message: str, entry_type: str = "info") -> None:
    """Internal helper to create a log entry."""
    log = LogEntry(
        client_id=client_id,
        automation_instance_id=automation_instance_id,
        entry_type=entry_type,
        message=message,
    )
    db.session.add(log)
    db.session.commit()


def run_lead_capture(ai: AutomationInstance, lead: Lead) -> None:
    """Handle the 'Universal Lead Capture' automation.

    Sends a notification email to client users and logs the event.
    """
    # Send email to all client users
    recipients = [user.email for user in lead.client.users if user.active]
    subject = f"New lead captured: {lead.name}"
    body = f"A new lead has been captured.\n\nName: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone or 'N/A'}\nSource: {lead.source}"
    send_email(recipients, subject, body)
    _log(lead.client_id, ai.id, f"Lead capture automation executed for lead {lead.id}")


def run_appointment_helper(ai: AutomationInstance, job: Job) -> None:
    """Handle the 'Appointment Helper' automation.

    Sends a confirmation email to the lead (if present) or client users and logs the event.
    """
    subject = f"Appointment confirmed: {job.title}"
    body = f"Your appointment '{job.title}' has been scheduled for {job.scheduled_time.strftime('%Y-%m-%d %H:%M') if job.scheduled_time else 'TBD'}."
    recipients = []
    if job.lead:
        recipients.append(job.lead.email)
    else:
        recipients.extend([u.email for u in job.client.users if u.active])
    send_email(recipients, subject, body)
    _log(job.client_id, ai.id, f"Appointment helper automation executed for job {job.id}")


def run_follow_up_sequence(ai: AutomationInstance) -> None:
    """Handle the 'Follow‑Up Email Sequence' automation.

    Finds stale leads (status 'new' and older than X days) and sends follow‑up emails.  Stops on status change.
    """
    stale_days = 3
    cutoff = datetime.utcnow() - timedelta(days=stale_days)
    client = ai.client
    leads = Lead.query.filter_by(client_id=client.id, status="new").filter(Lead.created_at < cutoff).all()
    for lead in leads:
        subject = f"Checking in: still interested in our services?"
        body = f"Hi {lead.name},\n\nWe noticed you reached out but haven't scheduled an appointment yet. Let us know if you have any questions or would like to book a time."
        send_email(lead.email, subject, body)
        _log(client.id, ai.id, f"Follow‑up email sent to lead {lead.id}")
    if not leads:
        _log(client.id, ai.id, "Follow‑up sequence executed: no stale leads found")


def run_review_request(ai: AutomationInstance, job: Job) -> None:
    """Handle the 'Job Completion → Review Request' automation.

    Sends a review request email to the lead associated with a completed job.
    """
    if not job.lead:
        return
    subject = f"How did we do? Please leave a review"
    body = f"Hi {job.lead.name},\n\nYour job '{job.title}' has been completed. We'd love to hear your feedback! Please reply with your review."
    send_email(job.lead.email, subject, body)
    _log(job.client_id, ai.id, f"Review request sent for job {job.id}")


def run_daily_digest(ai: AutomationInstance) -> None:
    """Handle the 'Daily Digest' automation.

    Compiles a summary of daily activity and emails it to client users.
    """
    client = ai.client
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    leads_today = Lead.query.filter_by(client_id=client.id).filter(Lead.created_at >= today_start).count()
    jobs_today = Job.query.filter_by(client_id=client.id).filter(Job.created_at >= today_start).count()
    automations_running = AutomationInstance.query.filter_by(client_id=client.id, enabled=True).count()
    summary = (
        f"Daily Digest:\n\nLeads Today: {leads_today}\nJobs Created Today: {jobs_today}\n"
        f"Automations Running: {automations_running}\nTime Saved: (estimated)"
    )
    recipients = [u.email for u in client.users if u.active]
    send_email(recipients, "Daily Digest", summary)
    _log(client.id, ai.id, "Daily digest sent")