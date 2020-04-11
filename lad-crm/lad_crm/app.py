from flask import Flask
from .views import init_blueprints


def init_app():
    """Initialize Flask application

    :return Flask: initialized application
    """
    app = Flask(__name__)

    # register blueprints
    init_blueprints(app)

    return app
