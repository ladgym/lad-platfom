import os


class LadCrmConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "lad-crm-secret")


class ProductionConfig(LadCrmConfig):
    pass


class DevelopmentConfig(LadCrmConfig):
    WTF_CSRF_ENABLED = False
    TESTING = True


class TestConfig(LadCrmConfig):
    WTF_CSRF_ENABLED = False


CONFIG = {"development": DevelopmentConfig, "production": ProductionConfig}


def init_config(app):
    """

    :param Flask app: The Flask application
    :return:
    """
    config_name = app.config.get("ENV", "production")
    app.config.from_object(CONFIG.get(config_name))
    return app
