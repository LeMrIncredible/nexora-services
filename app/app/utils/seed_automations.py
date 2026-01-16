"""
Seed Nexora automation templates (V1)
Creates the 5 required automation templates if missing.
"""

from __future__ import annotations

#from app.app.extensions import db
#from app.app.models import AutomationTemplate

# Import db directly from the parent package. The db object is defined in
# app/app/__init__.py during application setup, so we can import it from
# the package namespace instead of an "extensions" module. Importing via
# ``..extensions`` previously failed because the extensions module no longer
# exists.
from .. import db
from ..models import AutomationTemplate
TEMPLATES = [
    {
        "slug": "lead-capture",
        "name": "Universal Lead Capture",
        "description": "Creates lead, tags source, sends notification email, logs action.",
        "default_enabled": True,
    },
    {
        "slug": "estimate-generator",
        "name": "Estimate Generator",
        "description": "Generates quick estimate from intake details and logs action.",
        "default_enabled": False,
    },
    {
        "slug": "invoice-tracking",
        "name": "Invoice Tracking & Reminders",
        "description": "Creates invoice record + reminder cadence, logs each attempt.",
        "default_enabled": False,
    },
    {
        "slug": "reputation-followup",
        "name": "Job Completion → Review Request",
        "description": "Sends review request when job completes, logs action.",
        "default_enabled": False,
    },
    {
        "slug": "smart-booking",
        "name": "Appointment Helper (Smart Booking)",
        "description": "Confirms appointments and schedules jobs, logs updates.",
        "default_enabled": False,
    },
]

def seed_automation_templates() -> None:
    changed = False
    for t in TEMPLATES:
        existing = AutomationTemplate.query.filter_by(slug=t["slug"]).first()
        if not existing:
            db.session.add(
                AutomationTemplate(
                    slug=t["slug"],
                    name=t["name"],
                    description=t["description"],
                    default_enabled=t["default_enabled"],
                )
            )
            changed = True
    if changed:
        db.session.commit()
