from flask import Blueprint, render_template

skier = Blueprint("skier", __name__)

@skier.route("/about")
def about():
    return render_template("about.html")