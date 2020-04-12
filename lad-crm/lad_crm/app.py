from flask import Flask
from lad_crm.views import init_blueprints
from lad_crm.settings.config import init_config


def init_app():
    """Initialize Flask application

    :return Flask: initialized application
    """
    app = Flask(__name__)

    # initialize app configuration
    init_config(app)

    # register blueprints
    init_blueprints(app)

    return app
