from flask import Blueprint, render_template

frontend = Blueprint("frontend", __name__)

@frontend.route("/about")
def about():
    return render_template("about.html",
        add_link="javascript:$(\"#addDialogue\").slideDown();",
        search_link="")
        #currkeys=len(gpg.list_keys())) # This is commented out right now because I can't think of a fast way to implement it.
                                        # If you can think of a better way to do this than loading all keys into memory, go ahead.

@frontend.route("/search")
def search():
    return render_template("search.html")