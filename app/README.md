# Nexora V1

Nexora is a multi‑tenant SaaS IT and automation platform for small home‑services businesses.  It replaces the need for a human administrative assistant by running background automations (starting with Google Workspace workflows) while providing a transparent, professional command‑center dashboard that proves value and builds trust.

This repository contains the full source code for the Nexora V1 application, including documentation and deployment instructions.

## Contents

* [`run.py`](run.py) – entry point for running the Flask application.
* [`app/`](app) – the main application package containing models, routes, templates, and utilities.
* [`requirements.txt`](requirements.txt) – Python dependencies needed to run Nexora V1.
* [`docs/`](docs) – additional documentation, including design decisions, architecture overview, data model explanations, and testing notes.

## What the app does

Nexora V1 provides a low/no‑code monolithic platform with the following features:

* **Authentication and roles**: Users can sign in as either a client user or a Nexora administrator. Role‑based access control enforces strict separation of data between tenants.
* **Client command center**: Clients log in to view their personalized dashboard, leads, jobs, and activity logs. The dashboard layout is saved per client and can be rearranged or hidden.
* **Admin console**: Nexora administrators can create and manage client accounts, assign portfolios, configure automations, view logs and errors, and edit automation templates.
* **Public lead capture**: Each client has a public lead form accessible at `/lead/<clientSlug>` that can be shared via embed or link. Submissions create leads, tag the source, send notifications, and record logs.
* **Automations**: Five configurable automation templates are provided (Lead Capture, Appointment Helper, Follow‑Up Sequence, Job Completion → Review Request, and Daily Digest). Automations are toggleable per client and run as scheduled jobs via APScheduler. Logging is built in to track success and failure.
* **Google Workspace integration**: Stub support for Gmail, Calendar, and Sheets is provided via the `IntegrationCredential` model. Real OAuth integration can be added via environment variables and the Google API client libraries.
* **Responsive UI**: Pages use Bootstrap for responsive design, ensuring the platform works on both web and mobile.

## How to deploy

1. **Install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables:** Copy `.env.example` to `.env` and edit the values. At minimum, you must provide a `SECRET_KEY` for session security. If you intend to use real Google Workspace integration, set the relevant OAuth credentials.

3. **Initialize the database:**

   ```bash
   flask db upgrade
   # create default portfolio and admin user (see docs/setup.md)
   ```

4. **Run the application:**

   ```bash
   flask run
   ```

   By default the app runs on `http://localhost:5000`. Use `--host=0.0.0.0` to listen on all interfaces.

5. **Access the platform:**

   * Clients sign in via `/login` and are redirected to their dashboard.
   * Administrators sign in with an account flagged as `role='admin'` and visit `/admin`.
   * Public lead forms are available at `/lead/<client_slug>`.

## How to add a new client

1. Sign in as an administrator and navigate to the **Client Manager** in the admin console (`/admin/clients`).
2. Click **Create Client** and fill out the form. The system will automatically generate a unique slug for the public lead form.
3. Assign the built‑in **Home Services Portfolio** and enable the desired automation templates.
4. Create one or more client users associated with the new client so they can log in. Client users cannot access admin functionality or other clients’ data.

## How to enable automations

1. Each automation template (Lead Capture, Appointment Helper, Follow‑Up Sequence, Job Completion → Review Request, Daily Digest) can be enabled or disabled per client from the **Automations** tab of the client detail page in the admin console.
2. The scheduler runs in the background using APScheduler. The daily digest and follow‑up sequence jobs are triggered automatically at midnight. Trigger‑based automations (Lead Capture, Appointment Helper, Job Completion → Review Request) are invoked when relevant events occur.

## Known limitations

* The Google Workspace integration is stubbed in this version. OAuth flows and API calls are not fully implemented but can be added by providing the appropriate credentials and using Google’s client libraries.
* Email sending is simulated by logging. Replace the `send_email` utility in `app/utils/email.py` with a real email service to deliver messages.
* SMS and voice calling are not part of V1 but are planned for V1.1.
* This monolithic implementation uses SQLite by default for simplicity. For production deployments, configure a more robust database (e.g. PostgreSQL) via SQLAlchemy settings.

## Architecture Summary

Nexora V1 is built as a Flask application with a monolithic architecture. It uses SQLAlchemy for data persistence and APScheduler for background job scheduling. The admin console and client portal are separate blueprints with distinct routes and templates. The UI leverages Bootstrap for a consistent look and responsive design. Authentication is handled by Flask‑Login, and roles are enforced via decorators.

The data model supports users, clients, portfolios, automation templates and instances, leads, jobs, logs, and integration credentials. Relationships enforce tenant isolation by scoping all relevant models to a client.

## Security notes

* Sessions are protected by a secret key stored in an environment variable.
* Passwords are hashed using `passlib` before storage.
* Role‑based access control ensures that client users cannot access admin routes or data belonging to other clients.
* Inputs from the public lead form are validated and sanitized to mitigate injection attacks.
* CSRF protection is enabled on all forms.

## Launch checklist

1. **Deploy the code** to a server and configure a domain with HTTPS.
2. **Install dependencies** and set environment variables on the server.
3. **Run database migrations** to prepare the schema.
4. **Create the default portfolio** and at least one admin user.
5. **Test role‑based access control** and basic workflows (lead capture, job scheduling, automation toggling).
6. **Enable daily scheduler** (APScheduler) in production to run automations.
7. **Document credentials** for Google OAuth integration (optional).
8. **Backup strategy**: set up regular database backups and log retention policies.

For additional details see the documentation in [`docs/`](docs).
