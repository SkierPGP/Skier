from flask import Blueprint, render_template

frontend = Blueprint("frontend", __name__)

@frontend.route("/about")
def about():
    return render_template("about.html")

@frontend.route("/submit")
def submit():
    return render_template("submit.html")