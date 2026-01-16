# Deployment Guide

This guide explains how to deploy the **Nexora** project into a production environment.  Nexora is a *monorepo* containing two distinct applications:

1. **Marketing website** – a Node.js application that serves static pages (`public/`), the free audit form and exposes simple HTTP endpoints (under `/api`).  It uses no third‑party dependencies so the build step is trivial.
2. **Client portal & admin console** – a Python/Flask application located under `app/`.  This application provides authentication, multi‑tenant dashboards, admin functionality and background automation scheduling.

You can deploy these applications as separate services (recommended) or combine them behind a reverse proxy.  The instructions below cover local development, deployment on Render and production best practices.

## 1. Prepare the Environment

1. **Clone the repository** to your server and change into the project directory:

   ```bash
   git clone <your-fork-url> nexora
   cd nexora
   ```

2. **Create environment files**.  There are two `.env.example` files:

   * **Root `.env.example`** – used by the Node.js marketing site.  Copy it to `.env` and set values such as `CLIENT_NAME`, `CLIENT_EMAIL`, `CLIENT_PHONE` and, importantly, `PORTAL_URL`.  `PORTAL_URL` should point to the login page of the client portal (e.g. `https://app.yourdomain.com/login`).  When the portal and marketing site live on the same domain you can set it to `/login`.
   * **`app/.env.example`** – used by the Flask portal.  Copy it to `app/.env` and set at least a `SECRET_KEY` and `DATABASE_URL`.  See the comments in that file for optional email/OAuth configuration.

   Do not commit `.env` or `app/.env` to version control.

3. **Install runtime dependencies** for the portal (Python) if you plan to run it locally:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r app/requirements.txt
   ```

   The marketing site does not require package installation because it uses only built‑in Node.js modules.

## 2. Running Locally

### Marketing Site (Node.js)

To launch the marketing website locally run:

```bash
PORT=3000 node server.js
```

This will serve the static site on `http://localhost:3000`.  The `PORTAL_URL` defined in `.env` will be injected into the HTML for the **Client Portal** button.  Modify `PORTAL_URL` in `.env` if your portal runs on a different domain or port.

For production deployments you should run the Node process under a supervisor such as [`pm2`](https://pm2.keymetrics.io/) or `systemd` to ensure reliability.

### Client Portal & Admin Console (Python/Flask)

Within your virtual environment, start the Flask application via Gunicorn (recommended) or the built‑in server:

```bash
export FLASK_APP=app.run:app
export FLASK_ENV=production
cd app
gunicorn -b 0.0.0.0:8000 run:app
```

or for quick development:

```bash
python app/run.py
```

The portal will be available on `http://localhost:8000`.  Client users can log in at `/login` and administrators at `/login` as well.  Use Flask‑Migrate to set up the database if you are not using the default SQLite file.

## 3. Deploying on Render

The repository includes a [`render.yaml`](render.yaml) file that defines two Render **Web Services**: one for the marketing site and one for the portal.  When you push this repository to a connected GitHub account, Render will offer to create services based on this configuration.

### Marketing Service

* **Environment**: `node`
* **Build Command**: Not required because the site uses only built‑in modules
* **Start Command**: `node server.js`
* **Environment Variables**:
  - `PORT`: The port Render assigns to the service (automatically injected)
  - `PORTAL_URL`: Set this to the URL of your portal service (e.g. `https://nexora-portal.onrender.com/login`).  This value is injected into the HTML at runtime.

### Portal Service

* **Environment**: `python`
* **Build Command**: `pip install -r app/requirements.txt`
* **Start Command**: `gunicorn -b 0.0.0.0:$PORT app.run:app`
* **Environment Variables**:
  - `PORT`: Render‑provided port
  - `SECRET_KEY`: A strong secret for session signing (mark this as a secret in Render)
  - `DATABASE_URL`: Connection string for the SQLAlchemy database (e.g. `sqlite:///nexora.db` for local file or a PostgreSQL URI)

  - `DEFAULT_ADMIN_EMAIL` (optional): Email address for the first administrator.  On first run, if the portal has no admin users, the application will create one using this address and the `DEFAULT_ADMIN_PASSWORD`.  Defaults to `admin@example.com`.
  - `DEFAULT_ADMIN_PASSWORD` (optional): Password for the first administrator.  Defaults to `changeme`.  **Change this** to a strong password in production.

Render will automatically build and deploy each service.  When both are live, set the `PORTAL_URL` variable on the marketing service to the portal service’s public URL.  The **Client Portal** button on the home page will then navigate to the correct login page.

## 4. Additional Configuration

* **Google Workspace & Email** – To enable lead storage in Google Sheets or send real emails, provide a Google service account JSON file and update `GOOGLE_SERVICE_ACCOUNT_KEYFILE`, `LEADS_SHEET_ID`, `GMAIL_USER` and `GMAIL_PASS` in `.env`.  See `GOOGLE_WORKSPACE_SETUP.md` for detailed setup instructions.
* **Database & Migrations** – The Flask portal uses SQLite by default.  In production you should configure `DATABASE_URL` to point to a persistent database (e.g. PostgreSQL).  Use Flask‑Migrate (`flask db upgrade`) to apply migrations.
* **Secrets** – Never commit real credentials.  Use Render’s secret management or your host’s equivalent to set sensitive values like `SECRET_KEY` and Gmail passwords.

## 5. Updating the Application

When you make changes to the code:
1. Commit and push your changes to the repository.
2. Render will automatically build and redeploy the affected services based on `render.yaml`.  Alternatively, if running on your own server, pull the changes and restart the Node and Gunicorn processes.

## 6. Troubleshooting

* **Website loads but portal button does nothing** – Check that `PORTAL_URL` is defined in your marketing service’s environment.  The server replaces `%%PORTAL_URL%%` in `public/index.html` with this value.
* **Portal fails to start on Render** – Ensure that `pip install -r app/requirements.txt` completes successfully and that `DATABASE_URL` is set.  Render injects a `PORT` environment variable automatically; do not hardcode the port.
* **Python migrations missing** – Run `flask db upgrade` after deploying the portal service to initialise the database.
* **Automations not running** – Verify that the scheduler is running (it starts when the app initialises) and that each automation instance is enabled via the admin console.

## 7. Next Steps

This deployment guide covers the essentials.  For a production‑grade setup you should also:

* Terminate SSL/TLS using a reverse proxy (e.g. Nginx) or enable HTTPS on Render.
* Configure backups and monitoring for your database.
* Implement proper logging and error reporting.
* Harden the portal by enabling CSRF protection, rate limiting and secure session handling.

By following these steps you can take Nexora from development to production with confidence.  If you encounter issues not covered here, consult Render’s documentation or seek professional assistance.
