import os

# todo, is this needed?
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Other configs inherit those.
    """

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV_TYPE = "development"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL") or ""
    )
    SECRET_KEY = os.environ.get("SECRET_KEY") or "bla" * 10


class TestingConfig(Config):
    ENV_TYPE = "testing"
    DEBUG = True
    # otherwise form submits won't work
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL")
        or "postgresql://localhost"
    )
    SECRET_KEY = os.environ.get("TEST_SECRET_KEY") or "bla" * 10


class ProductionConfig(Config):
    ENV_TYPE = "production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("PROD_SECRET_KEY")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
