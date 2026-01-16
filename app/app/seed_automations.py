"""
Seed Nexora automation templates (V1)
Creates the 5 required automation templates if missing.
"""

from __future__ import annotations

"""
Seed Nexora automation templates (V1)

This module defines a function to populate the database with default
automation templates.  To avoid circular imports during app startup,
the function accepts the SQLAlchemy database instance as an argument
and imports models within the function body.  See the application
factory in ``app/app/__init__.py`` for the invocation.
"""

# Predefined list of automation templates.  Each template dictionary
# contains the slug, human‑readable name, description, and whether the
# automation should be enabled by default for new clients.
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

def seed_automation_templates(db) -> None:
    """
    Create missing automation templates in the database.

    Args:
        db: The SQLAlchemy database instance from the application factory.

    This function defers importing the AutomationTemplate model until
    execution time to avoid circular import issues.  It iterates over
    the predefined ``TEMPLATES`` list and inserts any missing
    templates into the database.  If at least one template is added,
    the changes are committed.
    """
    # Import within the function body to avoid circular imports.  The
    # models module defines the AutomationTemplate class using the
    # ``db`` instance from the application factory.  At this point in
    # application setup, db has been initialised on the Flask app.
    from ..models import AutomationTemplate

    changed = False
    for t in TEMPLATES:
        # Check if a template with the same slug already exists
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
