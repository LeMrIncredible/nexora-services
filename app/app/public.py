"""
Public lead form blueprint.

This blueprint serves the publicly accessible lead capture form for each
client.  When a form is submitted, a `Lead` record is created,
associated with the specified client, and the `lead_capture`
automation is invoked if enabled.
"""

from flask import Blueprint, render_template, abort, redirect, url_for, flash, request
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Optional
from flask_wtf import FlaskForm

from .models import Client, Lead, AutomationInstance, AutomationTemplate
from . import db
from .utils.automations import run_lead_capture

public_bp = Blueprint("public", __name__, url_prefix="")


class LeadForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional()])
    submit = SubmitField("Submit")


@public_bp.route("/lead/<client_slug>", methods=["GET", "POST"])
def lead_form(client_slug: str):
    client = Client.query.filter_by(slug=client_slug).first()
    if not client:
        abort(404)

    form = LeadForm()
    if form.validate_on_submit():
        lead = Lead(
            client=client,
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            source=request.args.get("src") or "public_form",
        )
        db.session.add(lead)
        db.session.commit()
        # Invoke lead capture automation if enabled
        ai = (
            AutomationInstance.query.join(AutomationInstance.template)
            .filter(
                AutomationInstance.client == client,
                AutomationInstance.enabled == True,
                AutomationTemplate.type == "lead_capture",
            )
            .first()
        )
        if ai:
            run_lead_capture(ai, lead)
        flash("Thank you! Your information has been submitted.", "success")
        return redirect(url_for("public.lead_form", client_slug=client_slug))

    return render_template("public/lead_form.html", client=client, form=form)