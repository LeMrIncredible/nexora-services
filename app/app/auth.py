"""
Authentication blueprint.

Provides routes for logging in and logging out.  User registration for
clients is handled by administrators in the admin console.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm

from .models import User
from . import db


auth_bp = Blueprint("auth", __name__, url_prefix="")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # Redirect already logged-in users based on role
        if current_user.is_admin():
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("client.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        print('FORM ERRORS:', form.errors)

        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or (url_for("admin.dashboard") if user.is_admin() else url_for("client.dashboard")))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))