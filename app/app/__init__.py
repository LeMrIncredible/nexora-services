"""
Application factory for Nexora.

This module sets up the Flask application, database, migrations,
login manager, CSRF protection, and background scheduler.  Blueprints
for authentication, public lead capture, client portal, and admin
console are registered here.
"""

import logging
import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from .utils.seed_automations import seed_automation_templates

# Initialize extensions without application context
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
scheduler = BackgroundScheduler(daemon=True)


def create_app(config_object: str | None = None) -> Flask:
    """Factory to create and configure the Flask application.

    Args:
        config_object: Optional import path to a configuration class.  If
            omitted, `nexora.config.Config` is used.

    Returns:
        A fully configured Flask application.
    """
    # Load environment variables from .env if present
    load_dotenv()
    app = Flask(__name__, instance_relative_config=False)
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        from config import Config

        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    scheduler.configure(timezone="UTC")

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Configure login
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from .models import User, create_default_portfolio

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return User.query.get(int(user_id))

    # Application context initialisation
    with app.app_context():
        # Create database tables if they do not exist
        db.create_all()
        # Ensure the default portfolio exists
        create_default_portfolio()
        # Seed default automation templates.  Pass the database instance
        # explicitly to avoid circular import issues.  See
        # app/app/utils/seed_automations.py for details.
        seed_automation_templates(db)


        # Register blueprints
        from .auth import auth_bp
        from .public import public_bp
        from .client.routes import client_bp
        from .admin.routes import admin_bp
        from .routes.automations import bp as automations_bp


        # Register automation blueprint.  Note: previous versions mistakenly
        # called `regiser_blueprint`, which resulted in the automations API not
        # being registered.  Use the correct `register_blueprint` method.
        app.register_blueprint(automations_bp)

        app.register_blueprint(auth_bp)
        app.register_blueprint(public_bp)
        app.register_blueprint(client_bp)
        app.register_blueprint(admin_bp)
  
     


        # Schedule background jobs
        from .utils.scheduler import schedule_jobs

        schedule_jobs(scheduler)

        # Start scheduler
        if not scheduler.running:
            scheduler.start()

        # Attach scheduler to app for later access (e.g. rescheduling)
        app.scheduler = scheduler

    return app
