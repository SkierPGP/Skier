from flask import Blueprint, request

from skier import pgp
from skier.keyinfo import KeyInfo

legacypks = Blueprint("pks", __name__)

@legacypks.route("/add", methods=["POST"])
def pksadd():
    keytext = request.form["keytext"]
    result = pgp.add_pgp_key(keytext)
    if result[0]:
        return "", 200, {"X-HKP-Results-Count": "1"}
    else:
        return "Key add failed", 400, {"X-HKP-Results-Count": "1"}

@legacypks.route("/lookup", methods=["GET"])
def pksgetkey():
    if 'op' in request.args and request.args.get("op") == "get":
        # Lookup the key
        keyid = request.args.get("search")
        if keyid is None or not keyid.startswith("0x"):
            return "Invalid key data", 401
        else:
            key = pgp.get_pgp_armor_key(keyid)
            if key: return key, 200, {"Cache-Control": "no-cache", "Pragma": "no-cache"}
            else: return "", 404
    elif 'op' in request.args and request.args.get("op") == "index":
        return pkssearch(request.args)
    else:
        return "Invalid request", 400

def format_pks(keys):
    # First, add header.
    # This comes in the format of "info:1:{number-of-keys}"
    data = ""
    data += "info:1:{}\n".format(keys.total)
    # Then, add the strings for each key.
    for key in keys.query.all():
        # Load keyinfo.
        newkey = KeyInfo.pgp_dump(key.armored)
        s1, s2 = newkey.to_pks()
        data += s1 + '\n' + s2 + '\n'
    return data

def pkssearch(rargs):
    keys = pgp.search_through_keys(rargs.get("search"))
    if not keys.total:
        return "No keys found", 404
    else:
        return format_pks(keys), 200, {"X-HKP-Results-Count": keys.total}