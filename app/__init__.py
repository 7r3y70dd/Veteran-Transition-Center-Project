import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        from app.models import TotalModel
        db.create_all()

        if TotalModel.query.first() is None:
            db.session.add(TotalModel(0.0, "Database created", datetime.date.today()))
            db.session.commit()

    return app