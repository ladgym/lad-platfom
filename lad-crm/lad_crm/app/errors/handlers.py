from flask import render_template, flash
from app import db
from app.errors import bp


#: to do make a custom error page
@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Внутрення ошибка сервера :(')
    return render_template('base.html', title='Внутрення ошибка сервера'), 500
