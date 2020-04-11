from .home import home as bp_home


def init_blueprints(app):
    """
    Registers existing Blueprints
    :param Flask app: The Flask application
    :return Flask: application with registered blueprints
    """

    app.register_blueprint(bp_home)

    return app
