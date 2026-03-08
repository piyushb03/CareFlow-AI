"""
CareFlow AI — Flask Application Factory
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from backend.extensions import db
from backend.routes.cases import cases_bp
from backend.routes.evaluation import evaluation_bp
from backend.routes.health import health_bp

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def create_app() -> Flask:
    app = Flask(__name__)

    # Resolve project root for absolute database path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_db = f"sqlite:///{os.path.join(project_root, 'careflow.db')}"

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB request limit

    # CORS — allow frontend dev server
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

    # Extensions
    db.init_app(app)

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(cases_bp, url_prefix="/api")
    app.register_blueprint(evaluation_bp, url_prefix="/api")

    # Create tables — import models so SQLAlchemy registers all table metadata
    with app.app_context():
        import backend.models  # noqa: F401
        db.create_all()

    return app
