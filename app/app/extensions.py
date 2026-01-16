"""
Extensions module for Nexora.

This module instantiates shared extensions (currently SQLAlchemy).
Defining extensions in a separate module breaks circular imports: other
modules can import ``db`` from ``app.extensions`` without triggering
the ``app`` package to be fully initialised.  See ``app/app/__init__.py``
for where the extensions are initialised on the Flask application.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance.  The application factory will
# initialise this instance with the Flask app.  Other modules should
# import ``db`` from ``app.extensions`` instead of instantiating their own
# SQLAlchemy object.
db: SQLAlchemy = SQLAlchemy()

__all__ = ["db"]