import json

from flask import Blueprint

from cfg import cfg
from skier import pgp, pgpactions

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

@pgpapi.route("/import/<keyserver>/<keyid>", methods=["POST"])
def importkey(keyserver, keyid):
    if not keyserver in cfg.config.sks_imports:
        if not keyserver in cfg.config.skier_imports:
            return json.dumps({"code": 2, "err": "Invalid keyserver"}), 400, {"Content-Type": "application/json"}
    key = pgpactions.import_key(keyserver=keyserver, keyid=keyid)
    if key == -2:
        return json.dumps({"code": 3, "err": "Could not connect"}), 400, {"Content-Type": "application/json"}
    elif key == -1:
        return json.dumps({"code": 1, "err": "Key not found"}), 404, {"Content-Type": "application/json"}
    elif key == -3:
        return json.dumps({"code": 4, "err": "Key invalid"}), 400, {"Content-Type": "application/json"}
    elif key == -4:
        return json.dumps({"code": 5, "err": "Key exists and unchanged"}), 400, {"Content-Type": "application/json"}
    elif key == 0:
        return json.dumps({"code": 0, "err": ""}), 200, {"Content-Type": "application/json"}
    else:
        return ""

@pgpapi.route("/importers")
def importers():
    return json.dumps(cfg.config.skier_imports + cfg.config.sks_imports)
