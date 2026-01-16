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
# contains the internal ``type`` identifier, human‑readable name and a
# description.  The ``type`` corresponds to the slug/identifier used
# throughout the rest of the codebase.  We do not include a
# ``default_enabled`` flag here because the AutomationTemplate model
# currently does not define such a field.  If enabling logic is needed
# by default, it should be handled at the AutomationInstance level.
TEMPLATES = [
    {
        "type": "lead-capture",
        "name": "Universal Lead Capture",
        "description": "Creates lead, tags source, sends notification email, logs action.",
    },
    {
        "type": "estimate-generator",
        "name": "Estimate Generator",
        "description": "Generates quick estimate from intake details and logs action.",
    },
    {
        "type": "invoice-tracking",
        "name": "Invoice Tracking & Reminders",
        "description": "Creates invoice record + reminder cadence, logs each attempt.",
    },
    {
        "type": "reputation-followup",
        "name": "Job Completion → Review Request",
        "description": "Sends review request when job completes, logs action.",
    },
    {
        "type": "smart-booking",
        "name": "Appointment Helper (Smart Booking)",
        "description": "Confirms appointments and schedules jobs, logs updates.",
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
        # Check if a template with the same type already exists
        existing = AutomationTemplate.query.filter_by(type=t["type"]).first()
        if not existing:
            db.session.add(
                AutomationTemplate(
                    type=t["type"],
                    name=t["name"],
                    description=t["description"],
                )
            )
            changed = True

    if changed:
        db.session.commit()
