from flask import Blueprint, render_template, url_for, request, redirect

from skier import pgp
from cfg import cfg
from skier.keyinfo import KeyInfo

frontend = Blueprint("frontend", __name__)
frontend_keys = Blueprint("user_display_keys", __name__)

@frontend.route("/")
def index():
    return render_template("index.html", host=cfg.config.hostname)

@frontend.route("/about")
def about():
    return render_template("about.html",
        add_link=url_for("frontend.add"),
        search_link=url_for("frontend.search"))
        #currkeys=len(gpg.list_keys())) # This is commented out right now because I can't think of a fast way to implement it.
                                        # If you can think of a better way to do this than loading all keys into memory, go ahead.

@frontend.route("/about/faq")
def faq():
    return render_template("about/faq.html")

@frontend.route("/about/pgp")
def whatispgp():
    return render_template("about/pgp.html")

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
            if imported[1] == -1:
                return render_template("submit.html", success=False, errormsg="Seems like an error happened importing your key. Double-check you copy/pasted it correctly.")
            elif imported[1] == -2:
                return render_template("submit.html", success=False, errormsg="Your key is already added on the server and is unchanged.")
        else:
            keyinfo = pgp.get_pgp_keyinfo(imported[1])
            return redirect(url_for("frontend.getkeyinfo", key=keyinfo.shortid, added=True)), 302
            #return render_template("keyinfo.html", added=True, key=keyinfo, keydata=key)


@frontend.route("/keyinfo/<key>", methods=["GET", "POST"])
def getkeyinfo(key: str):
    if key.startswith("0x"):
        key = key.replace("0x", "")
    # Keyinfo route.
    keydata = pgp.get_pgp_keyinfo(key)
    if request.args.get("added", False): added = True
    else: added = False
    if keydata:
        keyascii = pgp.get_pgp_armor_key(key)
        return render_template("keyinfo.html", added=added, key=keydata, keydata=keyascii, found=True)
    else:
        return render_template("keyinfo.html", found=False, keyid=key), 404


@frontend.route("/search")
def search():
    if 'keyid' in request.args:
        page = request.args.get("page", 1)
        try:
            page = int(page)
        except:
            page = 1
        # Pass a simple list of KeyInfos to the renderer, allowing the template to do the hard work.
        keys = pgp.search_through_keys(request.args.get("keyid", "0x12345678"), page=page)
        if not keys.total:
            page = 0
        return render_template("search.html", search=request.args.get('keyid'), keys=keys.items, keyinfo=KeyInfo,
                               page=page, maxpages=keys.pages, num_keys=keys.total)
    else:
        return render_template("search.html")

@frontend.route("/import")
def import_key():
    return render_template("import.html"), 200


@frontend_keys.route("/<keyid>")
def getkey(keyid):
    key = pgp.get_pgp_armor_key(keyid)
    if key:
        return key, 200, {"Content-Type": "text/plain"}
    else:
        return "No such key", 404, {"Content-Type": "text/plain"}


@frontend_keys.route("/<keyid>/dl/ascii")
def getkey_dl_ascii(keyid):
    key = pgp.get_pgp_armor_key(keyid)
    if key:
        return key, 200, {"Content-Type": "text/plain", "Content-Disposition": "attachment; filename={}.asc".format(keyid)}
    else:
        return "No such key", 404, {"Content-Type": "text/plain"}

#@frontend_keys.route("/<keyid>/dl/raw")
#def getkey_dl_raw(keyid):
#    key = pgp.get_pgp_armor_key(keyid)
#    if key:
#        return key, 200, {"Content-Type": "application/octet-stream", "Content-Disposition": "attachment; filename={}.gpg".format(keyid)}
#    else:
#        return "No such key", 404, {"Content-Type": "text/plain"}