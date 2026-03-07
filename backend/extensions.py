"""
CareFlow AI — Flask Extensions
Single module for shared extensions to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
