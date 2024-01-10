from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager().init_app(app)

    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    return app
