# Setup Guide for Nexora V1

Follow these steps to prepare Nexora for your first production deployment.

## 1. Install dependencies

Create a virtual environment and install the required Python packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure environment variables

Copy the `.env.example` file to `.env` and update the values.  At minimum you must set:

* `SECRET_KEY` – a random string used to secure sessions.
* `DATABASE_URL` – optional; defaults to a local SQLite database (`sqlite:///nexora.db`).  For production, point this to a PostgreSQL or MySQL database.

Example `.env`:

```bash
SECRET_KEY=supersecretkey
DATABASE_URL=sqlite:///nexora.db
```

## 3. Initialize the database

Run the migration commands to create the database schema:

```bash
flask db upgrade
```

The application automatically creates the default **Home Services Portfolio** and five automation templates if they do not already exist.

## 4. Create an admin user

Launch a Python shell or use a script to create the first administrator:

```python
from nexora.app import create_app, db
from nexora.app.models import User
app = create_app()
with app.app_context():
    admin = User(email="admin@example.com", role="admin")
    admin.set_password("changeme")
    db.session.add(admin)
    db.session.commit()
```

Now you can log in at `/login` with the admin credentials.

## 5. Run the application

Use the Flask CLI or run the `run.py` script:

```bash
flask run --host=0.0.0.0
```

or

```bash
python run.py
```

## 6. Create clients and users

1. Sign in as the admin user.
2. Navigate to the **Clients** section in the admin console.
3. Create a new client by providing a name and optional slug.  Slugs must be unique; if left blank, they are automatically generated based on the name.
4. After creating a client, add client users on the client detail page.  Client users cannot access the admin console or other clients’ data.

## 7. Enable or disable automations

Automations are created automatically for each client.  Administrators can enable or disable each automation from the client detail page.  The scheduler automatically updates when automations are toggled.

## 8. Scheduler

The background scheduler (APScheduler) runs in the Flask process.  It registers daily jobs for the **Follow‑Up Email Sequence** (runs at 00:30 UTC) and **Daily Digest** (runs at 01:00 UTC) for all clients that have those automations enabled.  Trigger‑based automations (Lead Capture, Appointment Helper, Review Request) are invoked when relevant events occur in the application.
