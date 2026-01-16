# What I Changed

## Root Causes

### Dead "Client Portal" Button
The marketing site (`public/index.html`) hard‑coded the portal link to `https://app.nexoraservices.info/auth/login`.  In our local and Render deployments that URL doesn’t exist, so the button effectively **did nothing**.  There was no way to configure the portal URL dynamically, so when the site was deployed on a different domain the link broke.  There was also no automated test to catch dead links.

### Render Deployment Failure
The repository is a **monorepo** containing a Node.js marketing site and a Python/Flask customer portal.  The original Render configuration attempted to deploy the entire repo as a single service using the Node build command.  This failed because Render ran `npm start` in the root directory, which only serves the marketing site and ignores the Python portal.  Furthermore, `server.js` bound to `localhost` instead of `0.0.0.0`, causing Render health checks to fail.  The portal’s Python dependencies were never installed and its start command wasn’t executed, so the `/login` route returned 404.

## Key Fixes & Changes

### Repository Structure & Scripts
- **Converted the monorepo into a dual‑service deployment.**  Added a `render.yaml` defining two services:
  - `nexora-website` – Node service that runs `node server.js` to serve the marketing site.  It sets an environment variable `PORTAL_URL` which the marketing site uses to link to the portal.
  - `nexora-portal` – Python (Flask) service that installs dependencies from `app/requirements.txt` and starts via `gunicorn --bind 0.0.0.0:$PORT app:app`.
- **Updated `server.js`** to listen on `process.env.PORT` and `0.0.0.0`.  Added logic to replace a `%%PORTAL_URL%%` placeholder in HTML files with the value of `process.env.PORTAL_URL` or a default `/login`.  This ensures the portal link is always correct for the current deployment.
- **Patched `public/index.html`** to include a placeholder for the portal link (`<a id="client-portal-link" href="%%PORTAL_URL%%">Client Portal</a>`) with documentation.  This dynamic replacement happens when the server serves the HTML.
- **Added `.env.example` entries** explaining the new `PORTAL_URL` variable for the marketing site and ensured Python’s `.env.example` contains `SECRET_KEY` and `DATABASE_URL`.
- **Fixed Flask blueprint bug** by correcting the misspelling `regiser_blueprint` → `register_blueprint` in `app/app/__init__.py`.  This unblocked registration of the `routes/automations.py` blueprint.
- **Added missing automations** by creating stub Python packages under `app/app/automations` (lead capture, estimate generator, invoice tracking, reputation follow‑up, smart booking).  These implement a `run()` function returning structured results and are mapped to slugs in `automations/runner.py`.
- **Updated deployment docs**.  Replaced the old single‑service instructions in `DEPLOYMENT.md` with steps for a multi‑service Render deployment, including environment variables, build/start commands, and local run instructions.

### Consistency & Housekeeping
- Added a placeholder replacement comment and ID to the portal link in `public/index.html`.
- Created `render.yaml` to avoid manual Render UI configuration and documented all required environment variables.
- Added `.gitignore` and `.env.example` entries for new configuration.
- Added test instructions in `DEPLOYMENT.md` to check for dead links and portal navigation.

### Flask Portal Improvements

During deployment of the Flask portal on Render we discovered additional problems, primarily around database seeding and circular imports.  These changes ensure the portal boots reliably in a multi‑worker environment:

* **Split extensions into a separate module.**  Introduced `app/app/extensions.py` with a single `db = SQLAlchemy()` instance.  This allows other modules to import `db` from `app.extensions` and breaks the circular dependency that previously occurred when `app/app/__init__.py` and `models.py` both tried to import each other.
* **Refactored `seed_automation_templates`.**  The original seeding function queried templates by `slug` and attempted to insert all missing records in one transaction.  When multiple Gunicorn workers started simultaneously, duplicate inserts triggered unique‑constraint violations on the `name` column and crashed the app.  We moved the function into `app/app/utils/seed_automations.py`, changed its signature to accept the database instance (`seed_automation_templates(db)`), deferred importing `AutomationTemplate` until inside the function, and implemented idempotent logic: it now checks for existing records by **name**, inserts missing records one by one, commits each insert immediately, and catches any `IntegrityError` to roll back and continue.  This makes seeding safe even when several workers start at once.
* **Updated application factory.**  Modified `app/app/__init__.py` to import `db` from `.extensions` rather than instantiating it locally, initialise it on the Flask app, and call `seed_automation_templates(db)` within the application context after creating tables and the default portfolio.  This change also corrected the blueprint registration bug noted above.
* **Removed duplicate seeding logic.**  The repository originally contained two `seed_automations.py` files (`app/app/seed_automations.py` and `app/app/utils/seed_automations.py`) with conflicting implementations.  We standardised on the new `utils` version and removed the redundant top‑level module to avoid confusion.

## Remaining Work
 - The portal uses Bootstrap while the marketing site uses Tailwind.  A full theme unification would require migrating the portal templates to Tailwind or adding custom CSS; this was left as a future improvement.
 - Some automations are stub implementations; production versions should integrate with external services (Google Workspace, billing systems, etc.).
 - The `nexoraservices.info` domain currently points to the legacy `nexora-services` service on Render.  To make the new marketing site accessible via the custom domain, the DNS or Render domain settings should be updated to map `nexoraservices.info` to the `nexora-website` service.  This requires access to the domain registrar or Render's custom domain configuration, which was beyond the scope of this fix.

