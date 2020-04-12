from flask import Blueprint, render_template, flash, redirect

from lad_crm.forms.public.login import LoginForm


public_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static")


@public_bp.route("/")
@public_bp.route("/index")
def home_page():
    return render_template("public/index.html")


@public_bp.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Login requested for email {form.email.data}, remember={form.remember_me.data}")
        return redirect("/index")
    return render_template("public/login.html", title="Sign In", form=form)
