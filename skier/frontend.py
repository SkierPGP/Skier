from flask import Blueprint, render_template, url_for, request

frontend = Blueprint("frontend", __name__)

@frontend.route("/about")
def about():
    return render_template("about.html",
        add_link=url_for("frontend.add"),
        search_link=url_for("frontend.search"))
        #currkeys=len(gpg.list_keys())) # This is commented out right now because I can't think of a fast way to implement it.
                                        # If you can think of a better way to do this than loading all keys into memory, go ahead.
@frontend.route("/add")
def add():
    return "", 200

@frontend.route("/search")
def search():

    if 'keyid' in request.args:
        return render_template("search.html", search=request.args.get('keyid'))
    else:
        return render_template("search.html")