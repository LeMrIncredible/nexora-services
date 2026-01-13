"""
Database models for Nexora V1.

These classes define the core data structures for users, clients,
portfolios, automation templates and instances, leads, jobs,
log entries, and integration credentials.  Relationships enforce
tenant isolation and allow administrators to manage clients while
restricting client users to their own data.
"""

from __future__ import annotations

import json
import string
import random
from datetime import datetime
from typing import Any, Dict, Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from . import db


def _random_slug(length: int = 8) -> str:
    """Generate a random slug consisting of lowercase letters and digits."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=length))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'client'
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship("Client", back_populates="users")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_client_user(self) -> bool:
        return self.role == "client"

    def get_id(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"


class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"))
    dashboard_layout = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship("User", back_populates="client", cascade="all, delete-orphan")
    portfolio = db.relationship("Portfolio", back_populates="clients")
    automation_instances = db.relationship(
        "AutomationInstance", back_populates="client", cascade="all, delete-orphan"
    )
    leads = db.relationship("Lead", back_populates="client", cascade="all, delete-orphan")
    jobs = db.relationship("Job", back_populates="client", cascade="all, delete-orphan")
    logs = db.relationship("LogEntry", back_populates="client", cascade="all, delete-orphan")
    credentials = db.relationship(
        "IntegrationCredential", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Client {self.name}>"


class Portfolio(db.Model):
    __tablename__ = "portfolio"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clients = db.relationship("Client", back_populates="portfolio")
    templates = db.relationship(
        "AutomationTemplate", back_populates="portfolio", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Portfolio {self.name}>"


class AutomationTemplate(db.Model):
    __tablename__ = "automation_template"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # internal identifier (e.g. lead_capture)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolio.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    portfolio = db.relationship("Portfolio", back_populates="templates")
    instances = db.relationship(
        "AutomationInstance", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AutomationTemplate {self.type}>"


class AutomationInstance(db.Model):
    __tablename__ = "automation_instance"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey("automation_template.id"), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship("Client", back_populates="automation_instances")
    template = db.relationship("AutomationTemplate", back_populates="instances")
    logs = db.relationship(
        "LogEntry", back_populates="automation_instance", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AutomationInstance {self.template.type} enabled={self.enabled}>"


class Lead(db.Model):
    __tablename__ = "lead"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=True)
    source = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(40), default="new")  # new, scheduled, stale, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    client = db.relationship("Client", back_populates="leads")
    jobs = db.relationship("Job", back_populates="lead")

    def __repr__(self) -> str:
        return f"<Lead {self.name} status={self.status}>"


class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(40), default="scheduled")  # scheduled, completed
    scheduled_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    client = db.relationship("Client", back_populates="jobs")
    lead = db.relationship("Lead", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job {self.title} status={self.status}>"


class LogEntry(db.Model):
    __tablename__ = "log_entry"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    automation_instance_id = db.Column(
        db.Integer, db.ForeignKey("automation_instance.id"), nullable=True
    )
    entry_type = db.Column(db.String(40), default="info")  # info, error
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship("Client", back_populates="logs")
    automation_instance = db.relationship("AutomationInstance", back_populates="logs")

    def __repr__(self) -> str:
        return f"<LogEntry {self.entry_type} {self.message[:20]}>"


class IntegrationCredential(db.Model):
    __tablename__ = "integration_credential"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    service = db.Column(db.String(40), nullable=False)  # gmail, calendar, sheets
    token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship("Client", back_populates="credentials")

    def __repr__(self) -> str:
        return f"<IntegrationCredential {self.service}>"


def create_default_portfolio() -> None:
    """Ensure that the default 'Home Services Portfolio' and automation templates exist."""
    # Check if the portfolio exists
    portfolio = Portfolio.query.filter_by(name="Home Services Portfolio").first()
    if not portfolio:
        portfolio = Portfolio(name="Home Services Portfolio", description="Default portfolio for home services clients.")
        db.session.add(portfolio)
        db.session.commit()

    # Predefined automation templates
    templates = [
        {
            "type": "lead_capture",
            "name": "Universal Lead Capture",
            "description": "Creates a lead from public form, tags the source, sends notification and logs action.",
        },
        {
            "type": "appointment_helper",
            "name": "Appointment Helper",
            "description": "Triggered by lead/job status or calendar event; sends confirmation email, updates record and logs action.",
        },
        {
            "type": "follow_up_sequence",
            "name": "Follow‑Up Email Sequence",
            "description": "Checks stale leads, sends follow‑ups, stops on status change, logs each attempt.",
        },
        {
            "type": "review_request",
            "name": "Job Completion → Review Request",
            "description": "On job completion, sends review request email and logs action.",
        },
        {
            "type": "daily_digest",
            "name": "Daily Digest",
            "description": "Sends a daily summary of activity via email and logs delivery.",
        },
    ]

    for tpl in templates:
        existing = AutomationTemplate.query.filter_by(type=tpl["type"]).first()
        if not existing:
            new_tpl = AutomationTemplate(
                name=tpl["name"], description=tpl["description"], type=tpl["type"], portfolio=portfolio
            )
            db.session.add(new_tpl)
    db.session.commit()
