from flask import Blueprint, request

from skier import pgp

legacypks = Blueprint("pks", __name__)

@legacypks.route("/add", methods=["POST"])
def pksadd():
    keytext = request.form["keytext"]
    result = pgp.add_pgp_key(keytext)
    if result:
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

def format_pks(keys: list):
    # First, add header.
    # This comes in the format of "info:1:{number-of-keys}"
    data = ""
    data += "info:1:{}\n".format(len(keys))
    # Then, add the strings for each key.
    for key in keys:
        s1, s2 = key.to_pks()
        data += s1 + '\n' + s2 + '\n'
    return data

def pkssearch(rargs):
    keys = pgp.search_through_keys(rargs.get("search"))
    if not keys:
        return "No keys found", 404
    else:
        return format_pks(keys), 200, {"X-HKP-Results-Count": len(keys)}