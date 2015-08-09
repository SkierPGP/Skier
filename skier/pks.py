from flask import Blueprint, request

from skier import pgp

legacypks = Blueprint("pks", __name__)

@legacypks.route("/add", methods=["POST"])
def add():
    keytext = request.form["keytext"]
    result = pgp.add_pgp_key(keytext)
    if result:
        return "", 200, {"X-HKP-Results-Count": "1"}

@legacypks.route("/lookup", methods=["GET"])
def getkey():
    # Lookup the key
    keyid = request.args.get("search")
    if keyid is None or not keyid.startswith("0x"):
        return "Invalid key data", 401
    else:
        key = pgp.get_pgp_armor_key(keyid)
        if key: return key, 200, {"Cache-Control": "no-cache", "Pragma": "no-cache"}
        else: return "", 404
