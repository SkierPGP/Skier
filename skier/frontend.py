from flask import Blueprint, render_template, url_for

from app import gpg

frontend = Blueprint("frontend", __name__)

@frontend.route("/about")
def about():
    return render_template("about.html",
        add_link="javascript:$(\"#addDialogue\").slideDown();",
        search_link="",
        currkeys=len(gpg.list_keys()))
