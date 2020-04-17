import datetime as dt
import sqlalchemy.orm as orm
import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app

from app import db

class User(UserMixin, db.Model):
    __tablename__ = "t_users"

    # columns
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    first_name = sa.Column(sa.String(32), nullable=False)
    last_name = sa.Column(sa.String(32), nullable=False)
    email = sa.Column(sa.String(64), unique=True, index=True, nullable=False)
    password_hash = sa.Column(sa.String(128), nullable=False)
    deleted = sa.Column(sa.Boolean, nullable=False, default=False)
    # this should be generated on the server, but it only works if the default is set here...
    datecreated = sa.Column(sa.DateTime, nullable=False, default=dt.datetime.utcnow)
    flask_admin = sa.Column(sa.Boolean, nullable=False, default=False)
    email_verified = sa.Column(sa.Boolean, nullable=False, default=False)

    def to_dict(self):
        return dict(
            id=self.id, first_name=self.first_name, last_name=self.last_name, email=self.email,
        )

    def __repr__(self):
        return "<User %r %r>" % (self.id, self.first_name)

    # Authentication related
    @property
    def password(self):
        raise AttributeError("password cannot be read")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        if self.id is None:
            raise ValueError("Need to have an id already")
        jwt = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"], expiration)
        return jwt.dumps({"confirm": self.id})

    def confirm_token(self, token):
        jwt = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        data = jwt.loads(token)
        if data.get("confirm") != self.id:
            return False
        else:
            self.email_verified = True
            return True

    def generate_reset_token(self, expiration=3600):
        if self.id is None:
            raise ValueError("Need to have an id already")
        jwt = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"], expiration)
        return jwt.dumps({"reset": self.id})

    def reset_password(self, token, new_password):
        jwt = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"])
        data = jwt.loads(token)
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def is_flask_admin(self):
        return self.flask_admin