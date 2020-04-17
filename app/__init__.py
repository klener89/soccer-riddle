import os
import logging
from app.config import config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, request as req

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.session_protection = "basic"
login_manager.login_view = "auth.login"

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv("FLASK_CONFIG") or "default"
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    app.logger.setLevel(logging.NOTSET)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.game import game

    app.register_blueprint(game, url_prefix="/")

    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(
            req.method, req.url, req.data, resp)
        )
        return resp

    return app
