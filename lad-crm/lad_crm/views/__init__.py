from lad_crm.views.public import public_bp


def init_blueprints(app):
    """
    Registers existing Blueprints
    :param Flask app: The Flask application
    :return Flask: application with registered blueprints
    """

    app.register_blueprint(public_bp)

    return app
