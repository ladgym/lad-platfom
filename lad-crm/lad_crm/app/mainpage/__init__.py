from flask import Blueprint

bp = Blueprint('mainpage', __name__)

from app.mainpage import routes
