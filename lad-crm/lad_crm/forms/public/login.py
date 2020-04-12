import wtforms as wtf

from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    email = wtf.StringField("email", validators=[DataRequired(), Email()])
    password = wtf.PasswordField("password", validators=[DataRequired()])
    remember_me = wtf.BooleanField("remember")
    submit = wtf.SubmitField("Sign In")
