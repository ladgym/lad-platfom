from flask import Blueprint

bp = Blueprint('managedb', __name__)

from app.managedb import routes
