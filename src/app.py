import os
from flask import Flask
from .models import db
from .routes import tasks_bp


def create_app(config=None):
    """Fábrica da aplicação Flask — permite instâncias distintas para teste e produção."""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, template_folder=template_dir)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techflow_tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'techflow-solutions-2024'
    app.config['JSON_SORT_KEYS'] = False

    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(tasks_bp)

    with app.app_context():
        db.create_all()

    return app
