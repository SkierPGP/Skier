from flask import Blueprint, render_template, url_for, request

from skier import pgp

frontend = Blueprint("frontend", __name__)
frontend_keys = Blueprint("user_display_keys", __name__)

@frontend.route("/about")
def about():
    return render_template("about.html",
        add_link=url_for("frontend.add"),
        search_link=url_for("frontend.search"))
        #currkeys=len(gpg.list_keys())) # This is commented out right now because I can't think of a fast way to implement it.
                                        # If you can think of a better way to do this than loading all keys into memory, go ahead.
@frontend.route("/add", methods=["GET", "POST"])
def add():
    # Get the key from the form
    key = request.form.get("enterkey")
    if not key:
        return render_template("submit.html")
    else:
        # Import the key
        imported = pgp.add_pgp_key(key)
        if not imported[0]:
            return render_template("submit.html", success=False)
        else:
            keyinfo = pgp.get_pgp_keyinfo(imported[1])
            return render_template("keyinfo.html", added=True, key=keyinfo, keydata=key)

@frontend.route("/search")
def search():
    if 'keyid' in request.args:
        # Pass a simple list of KeyInfos to the renderer, allowing the template to do the hard work.
        keys = pgp.search_through_keys(request.args.get("keyid", "0x12345678"))
        return render_template("search.html", search=request.args.get('keyid'), keys=keys)
    else:
        return render_template("search.html")

@frontend_keys.route("/<keyid>")
def getkey(keyid):
    key = pgp.get_pgp_armor_key(keyid)
    if key:
        return key, 200, {"Content-Type": "text/plain"}
    else:
        return "No such key", 404, {"Content-Type": "text/plain"}

@frontend_keys.route("/<keyid>/dl")
def getkey_raw(keyid):
    key = pgp.get_pgp_armor_key(keyid)
    if key:
        return key, 200, {"Content-Type": "text/plain", "Content-Disposition": "attachment; filename={}.asc".format(keyid)}
    else:
        return "No such key", 404, {"Content-Type": "text/plain"}