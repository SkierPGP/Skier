import json
import datetime

from flask import Blueprint, request

from cfg import cfg
from skier import pgp, pgpactions
import db

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

# Disabled for now due to we can't get the key raw.
#@pgpapi.route("/getkey/<keyid>/raw")
#def getkey_raw(keyid):
#    # Load the key.
#    key = pgp.get_pgp_key(keyid)
#    if key:
#        return key, 200, {"Content-Type": "application/octet-stream",
#                          "Content-Disposition": "attachment; filename=gpgkey.asc",
#                          "Cache-Control": "no-cache", "Pragma": "no-cache"}


@pgpapi.route("/search/<search_str>", methods=["GET", "POST"])
def searchkeys(search_str: str):
    # Get the count.
    count = request.args.get("count", 999)
    # Get the page
    page = request.args.get("page", 1)
    # Pass the search string to the database.
    results = pgp.search_through_keys(search_str, page=page, count=count)
    # Serialize the data into a JSON list of key ids.
    # Yes, this can hammer the server on shitty clients when they search.
    # But redis can pick up a lot of that slack.
    return json.dumps(
        {"count": results.total,
         "ids": [item.key_fp_id for item in results.items]}
    ), 200 if results.total else 404, {"Content-Type": "application/json"}


@pgpapi.route("/keyinfo/<keyid>", methods=["GET"])
def get_pgpapi_keyinfo(keyid):
    # Load the key info.
    key = pgp.get_pgp_keyinfo(keyid)
    # Check if it's none before proceeding
    if not key:
        return "{}", 404, {"Content-Type": "application/json"}
    # Otherwise, return the key info
    return key.to_json(), 200, {"Content-Type": "application/json"}


@pgpapi.route("/addkey", methods=["POST", "PUT"])
def addkey():
    # Read in the key data from the url arguments. Goes like ?keydata=.
    try:
        keydata = request.args["keydata"]
    except KeyError:
        return json.dumps({"error": 1, "msg": "no-key"}), 401, {"Content-Type": "application/json"}
    # Attempt to add the key.
    key = pgp.add_pgp_key(keydata)
    if key[0]:
        pgpactions.broadcast_add(key[2])
        return json.dumps({"error": 0, "msg": key[1]}), 200, {"Content-Type": "application/json"}
    else:
        return json.dumps({"error": key[1], "msg": "invalid-key-data"}), 401, {"Content-Type": "application/json"}


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

if cfg.config.pool_enabled.syncactions:
    @pgpapi.route("/sync/since")
    def check_keys_made_since():
        time = request.args.get("ts", datetime.datetime.utcnow().timestamp())
        try:
            dt = datetime.datetime.utcfromtimestamp(time)
        except TypeError: # or whatever
            dt = datetime.datetime.utcnow()
        # Query the database, check how many keys have been added since.
        keys_since = db.Key.query.filter(db.Key.added_time < dt)
        # Return a list of keys, and the count.
        # Assuming the other server has a correct API, it will take this result, and compare it with the other servers results.
        # Whichever has the highest number will be used.
        # This makes sure they are all synced every <x> hours.
        result = {"number": keys_since.count(), "keys": [key.key_fp_id for key in keys_since.all()]}
        return json.dumps(result), 200, {"Content-Type": "application/json", "X-Query-Timestamp": dt.timestamp()}

    @pgpapi.route("/sync/new", methods=["POST"])
    def handle_key_broadcast():
        # Recieve a new key broadcast.
        if 'key' in request.form:
            key = request.form["key"]
        else:
            # Prevent crashes from recieving an empty post.
            return
        res = pgp.add_pgp_key(key)
        if res[0]:
            return "", 200
        else:
            return "", 600 + res[1]
