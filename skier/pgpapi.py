import json
from flask import Blueprint

from skier import pgp

pgpapi = Blueprint("pgpapi", __name__)

@pgpapi.route("/getkey/<keyid>")
def getkey(keyid):
    # Load the key.
    key = pgp.get_pgp_armor_key(keyid)
    if key:
        return json.dumps({"key": key}), 200, {"Content-Type": "application/json",
                                               "Cache-Control": "no-cache", "Pragma": "no-cache"}
    else:
        return json.dumps({"key": None}), 404, {"Content-Type": "application/json",
                                                "Cache-Control": "no-cache", "Pragma": "no-cache"}

@pgpapi.route("/getkey/<keyid>/raw")
def getkey_raw(keyid):
    # Load the key.
    key = pgp.get_pgp_key(keyid)
    if key:
        return key, 200, {"Content-Type": "application/octet-stream",
                          "Content-Disposition": "attachment; filename=gpgkey.asc",
                          "Cache-Control": "no-cache", "Pragma": "no-cache"}