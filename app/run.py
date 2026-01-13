"""
Run Nexora V1.

This script creates the Flask application via the factory and runs
it with the built‑in development server.  For production
deployments, use a WSGI server such as Gunicorn or uWSGI.
"""

from app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)