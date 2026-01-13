"""
Admin console blueprint.

Provides routes for Nexora administrators to manage clients, users,
automation instances, and view logs or errors.  Access is
restricted to authenticated admin users.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Optional
from flask_wtf import FlaskForm

from ..models import (
    Client,
    User,
    Portfolio,
    AutomationTemplate,
    AutomationInstance,
    Lead,
    Job,
    LogEntry,
)
from .. import db
from ..utils.automations import run_follow_up_sequence, run_daily_digest
from ..utils.scheduler import schedule_jobs


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to restrict routes to admin users only."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Administrator access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


class ClientForm(FlaskForm):
    name = StringField("Client Name", validators=[DataRequired()])
    slug = StringField("Slug (leave blank to auto-generate)", validators=[Optional()])
    submit = SubmitField("Save")


class UserForm(FlaskForm):
    email = StringField("User Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Add User")


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Overview: list clients with basic stats
    clients = Client.query.all()
    client_stats = []
    for client in clients:
        leads_count = Lead.query.filter_by(client_id=client.id).count()
        jobs_count = Job.query.filter_by(client_id=client.id).count()
        user_count = len(client.users)
        client_stats.append({
            "client": client,
            "leads": leads_count,
            "jobs": jobs_count,
            "users": user_count,
        })
    # Count errors
    error_logs = LogEntry.query.filter_by(entry_type="error").count()
    return render_template("admin/dashboard.html", client_stats=client_stats, error_logs=error_logs)


@admin_bp.route("/clients", methods=["GET", "POST"])
@login_required
@admin_required
def clients():
    form = ClientForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip().lower() if form.slug.data else None
        if not slug:
            # Generate slug from name
            import re
            base_slug = re.sub(r"[^a-z0-9]+", "-", form.name.data.lower()).strip("-")
            slug = base_slug
            counter = 1
            while Client.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
        # Check for slug conflict
        if Client.query.filter_by(slug=slug).first():
            flash("Slug already exists. Please choose another.", "warning")
            return redirect(url_for("admin.clients"))
        # Assign default portfolio
        portfolio = Portfolio.query.filter_by(name="Home Services Portfolio").first()
        client = Client(name=form.name.data, slug=slug, portfolio=portfolio)
        db.session.add(client)
        db.session.commit()
        # Create automation instances for each template in the portfolio
        for template in portfolio.templates:
            ai = AutomationInstance(client=client, template=template, enabled=True)
            db.session.add(ai)
        db.session.commit()
        # Reschedule jobs after creating new instances
        schedule_jobs(current_app.scheduler)  # type: ignore
        flash("Client created successfully.", "success")
        return redirect(url_for("admin.clients"))
    clients = Client.query.all()
    return render_template("admin/clients.html", clients=clients, form=form)


@admin_bp.route("/clients/<int:client_id>", methods=["GET", "POST"])
@login_required
@admin_required
def client_detail(client_id: int):
    client = Client.query.get_or_404(client_id)
    user_form = UserForm()
    if user_form.validate_on_submit():
        # Create new client user
        if User.query.filter_by(email=user_form.email.data.lower()).first():
            flash("A user with that email already exists.", "warning")
        else:
            user = User(
                email=user_form.email.data.lower(),
                role="client",
                client=client,
            )
            user.set_password(user_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Client user created.", "success")
        return redirect(url_for("admin.client_detail", client_id=client_id))

    # Fetch automation instances for the client
    automations = AutomationInstance.query.filter_by(client_id=client.id).all()
    leads = Lead.query.filter_by(client_id=client.id).order_by(Lead.created_at.desc()).all()
    jobs = Job.query.filter_by(client_id=client.id).order_by(Job.created_at.desc()).all()
    logs = LogEntry.query.filter_by(client_id=client.id).order_by(LogEntry.created_at.desc()).limit(50).all()
    return render_template(
        "admin/client_detail.html",
        client=client,
        automations=automations,
        leads=leads,
        jobs=jobs,
        logs=logs,
        user_form=user_form,
    )


@admin_bp.route("/clients/<int:client_id>/automations/<int:instance_id>/toggle")
@login_required
@admin_required
def toggle_automation(client_id: int, instance_id: int):
    ai = AutomationInstance.query.filter_by(id=instance_id, client_id=client_id).first_or_404()
    ai.enabled = not ai.enabled
    db.session.commit()
    # Reschedule jobs when automations are toggled
    schedule_jobs(current_app.scheduler)  # type: ignore
    flash(f"Automation '{ai.template.name}' toggled {'on' if ai.enabled else 'off'}.", "info")
    return redirect(url_for("admin.client_detail", client_id=client_id))
