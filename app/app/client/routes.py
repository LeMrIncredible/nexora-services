"""
Client portal blueprint.

This blueprint contains routes for the client dashboard, leads,
jobs, logs, and settings.  Access is restricted to authenticated
client users.  Clients can view their data but cannot edit
automation logic.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_required, current_user
from wtforms import StringField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm

from ..models import Client, Lead, Job, AutomationInstance, AutomationTemplate, LogEntry
from .. import db
from ..utils.automations import run_appointment_helper, run_review_request


client_bp = Blueprint("client", __name__, url_prefix="")


def client_required(f):
    """Decorator to restrict routes to client users only."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_client_user():
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


class JobForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired()])
    lead_id = SelectField("Associated Lead", coerce=int, validators=[Optional()])
    scheduled_time = StringField("Scheduled Time (YYYY-MM-DD HH:MM)", validators=[Optional()])
    submit = SubmitField("Create Job")


class LayoutForm(FlaskForm):
    # Each module can be hidden or shown; order is determined by index in list
    kpi_visible = BooleanField("Show KPI Cards")
    automations_visible = BooleanField("Show Automations")
    activity_visible = BooleanField("Show Activity Feed")
    leads_visible = BooleanField("Show Leads Module")
    jobs_visible = BooleanField("Show Jobs Module")
    submit = SubmitField("Save Layout")


@client_bp.route("/dashboard")
@login_required
@client_required
def dashboard():
    client = current_user.client
    # Calculate KPIs
    from datetime import datetime
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day)
    leads_today = Lead.query.filter_by(client_id=client.id).filter(Lead.created_at >= start_of_day).count()
    jobs_scheduled = Job.query.filter_by(client_id=client.id, status="scheduled").count()
    automations_running = AutomationInstance.query.filter_by(client_id=client.id, enabled=True).count()
    # Estimate time saved as number of automations running * 5 minutes per run (placeholder)
    time_saved = automations_running * 5
    # Fetch automation instances
    automations = AutomationInstance.query.filter_by(client_id=client.id).all()
    # Latest logs
    logs = LogEntry.query.filter_by(client_id=client.id).order_by(LogEntry.created_at.desc()).limit(10).all()
    # Determine layout visibility
    layout = client.dashboard_layout or {}
    visible = layout.get("visible", {
        "kpi": True,
        "automations": True,
        "activity": True,
        "leads": True,
        "jobs": True,
    })
    return render_template(
        "client/dashboard.html",
        client=client,
        leads_today=leads_today,
        jobs_scheduled=jobs_scheduled,
        automations_running=automations_running,
        time_saved=time_saved,
        automations=automations,
        logs=logs,
        visible=visible,
    )


@client_bp.route("/leads")
@login_required
@client_required
def leads():
    client = current_user.client
    leads = Lead.query.filter_by(client_id=client.id).order_by(Lead.created_at.desc()).all()
    return render_template("client/leads.html", client=client, leads=leads)


@client_bp.route("/jobs", methods=["GET", "POST"])
@login_required
@client_required
def jobs():
    client = current_user.client
    form = JobForm()
    # Populate lead choices
    leads = Lead.query.filter_by(client_id=client.id).all()
    form.lead_id.choices = [(-1, "No Lead")] + [(lead.id, lead.name) for lead in leads]
    if form.validate_on_submit():
        job = Job(
            client_id=client.id,
            title=form.title.data,
            lead_id=form.lead_id.data if form.lead_id.data != -1 else None,
            status="scheduled",
        )
        # Parse scheduled_time if provided
        if form.scheduled_time.data:
            try:
                from datetime import datetime as _datetime

                job.scheduled_time = _datetime.strptime(form.scheduled_time.data, "%Y-%m-%d %H:%M")
            except ValueError:
                flash("Invalid date/time format. Use YYYY-MM-DD HH:MM", "warning")
        db.session.add(job)
        db.session.commit()
        # Invoke appointment helper automation if enabled
        ai = (
            AutomationInstance.query.join(AutomationInstance.template)
            .filter(
                AutomationInstance.client == client,
                AutomationInstance.enabled == True,
                AutomationTemplate.type == "appointment_helper",
            )
            .first()
        )
        if ai:
            run_appointment_helper(ai, job)
        flash("Job created successfully.", "success")
        return redirect(url_for("client.jobs"))
    # List jobs
    jobs = Job.query.filter_by(client_id=client.id).order_by(Job.created_at.desc()).all()
    return render_template("client/jobs.html", client=client, form=form, jobs=jobs)


@client_bp.route("/jobs/<int:job_id>/complete", methods=["POST"])
@login_required
@client_required
def complete_job(job_id: int):
    client = current_user.client
    job = Job.query.filter_by(id=job_id, client_id=client.id).first_or_404()
    job.status = "completed"
    db.session.commit()
    # Trigger review request automation if enabled
    ai = (
        AutomationInstance.query.join(AutomationInstance.template)
        .filter(
            AutomationInstance.client == client,
            AutomationInstance.enabled == True,
            AutomationTemplate.type == "review_request",
        )
        .first()
    )
    if ai:
        run_review_request(ai, job)
    flash("Job marked as completed.", "success")
    return redirect(url_for("client.jobs"))


@client_bp.route("/logs")
@login_required
@client_required
def logs():
    client = current_user.client
    logs = LogEntry.query.filter_by(client_id=client.id).order_by(LogEntry.created_at.desc()).limit(50).all()
    return render_template("client/logs.html", client=client, logs=logs)


@client_bp.route("/settings", methods=["GET", "POST"])
@login_required
@client_required
def settings():
    client = current_user.client
    layout = client.dashboard_layout or {}
    visible = layout.get("visible", {
        "kpi": True,
        "automations": True,
        "activity": True,
        "leads": True,
        "jobs": True,
    })
    form = LayoutForm(
        kpi_visible=visible.get("kpi", True),
        automations_visible=visible.get("automations", True),
        activity_visible=visible.get("activity", True),
        leads_visible=visible.get("leads", True),
        jobs_visible=visible.get("jobs", True),
    )
    if form.validate_on_submit():
        client.dashboard_layout = {
            "visible": {
                "kpi": form.kpi_visible.data,
                "automations": form.automations_visible.data,
                "activity": form.activity_visible.data,
                "leads": form.leads_visible.data,
                "jobs": form.jobs_visible.data,
            }
        }
        db.session.commit()
        flash("Layout saved.", "success")
        return redirect(url_for("client.settings"))
    return render_template("client/settings.html", client=client, form=form)