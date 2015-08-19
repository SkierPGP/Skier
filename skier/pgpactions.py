import datetime
import threading

import requests

import db
import cfg
from skier import pgp
from cfg import API_VERSION, SKIER_VERSION


def import_key(keyserver: str, keyid: str):
    """
    Attempts to import a key from the keyserver.
    :param keyserver: The keyserver to import from.
    :param keyid: The Key ID to import.
    :return:
        One of many codes:
        - 0: Success
        - -1: key not found
        - -2: Could not connect to keyserver
        - -3: Invalid key
        - -4: Already exists on server unchanged
    """
    # Check to see if the server is a skier server.
    is_skier = False
    try:
        if 'http://' not in keyserver and "https://" not in keyserver:
            keyserver = "http://" + keyserver
        r = requests.post(keyserver + "/skier", data=[API_VERSION,SKIER_VERSION])
        if r.status_code == 200:
            js = r.json()
            # Check the API version to make sure we're compatible.
            if js['api_version'] == API_VERSION:
                is_skier = True
    except:
        pass
    # Lookup the key.
    data = None
    if not is_skier:
        name = keyserver + "/pks/lookup"
        params = {"op": "get", "search": keyid, "options": "mr"}
        try:
            r = requests.get(name, params=params)
        except requests.exceptions.ConnectionError:
            return -2
        else:
            if r.status_code == 200:
                data = r.text
            elif r.status_code == 404:
                return -1
            elif r.status_code == 500:
                return -2
    else:
        name = keyserver + "/api/{}/getkey/{}".format(API_VERSION, keyid)
        try:
            r = requests.get(name)
        except requests.exceptions.ConnectionError:
            return -2
        else:
            if r.status_code == 200:
                data = r.json()['key']
            else:
                return -1
    if data:
        added = pgp.add_pgp_key(data)
        if added[0]:
            return 0
        else:
            if added[1] == -1:
                # invalid
                return -3
            elif added[1] == -2:
                # exists
                return -4

def synch_keys():
    print("Synching keys...")
    # We only synch once per bootup, because when a new key is added to any server, it's automatically distributed.
    # This ensures servers don't lag behind the rest of the pool.
    # Get the latest sync time.
    synch = db.Synch.query.order_by(db.Synch.synch_time.desc()).limit(1).first()
    if not synch:
        # No synchs has been made - this is the first one.
        dt = datetime.datetime(1970, 1, 1, 1, 0, 0)
    else:
        dt = synch.synch_time
    print("Synching since {}".format(dt))
    # Open up our servers list.
    synch_servers = cfg.cfg.config.keyservers_synch
    # Contact them, one-by-one.
    synch_dict = {}
    for server in synch_servers:
        assert isinstance(server, str)
        if not server.startswith("http"):
            # Force HTTPS by default, for security.
            server_url = "https://" + server
        else:
            server_url = server
            server = server.split("://")[1]

        try:
            r = requests.get(server_url + "/api/v{}/sync/since".format(cfg.API_VERSION), params={"ts": dt.timestamp()})
        except requests.exceptions.ConnectionError:
            # Whoops.
            continue

        if r.status_code != 200:
            # Server is either down or does not have pooling enabled.
            continue

        synch_dict[server] = r.json()

    chosen = (None, 0, [])
    # Choose server to synch from.
    for key, value in synch_dict.items():
        if value["number"] > chosen[1]:
            chosen = (key, value["number"], value["keys"])
        # Only the strongest and the fittest survive.

    # Begin downloading keys.
    for key in chosen[2]:
        base_url = "http://" + chosen[0] + "/api/v{}/getkey/{}".format(cfg.API_VERSION, key)
        try:
            r = requests.get(base_url)
        except requests.exceptions.ConnectionError:
            # what
            continue
        if r.status_code != 200:
            # This makes even less sense
            continue

        if not r.headers["content-type"] == "application/json":
            # This MAKES EVEN LESS SENSE
            continue

        keydata = r.json()["key"]
        pgp.add_pgp_key(keydata)

    # Update the synched table.
    new_synch = db.Synch()
    new_synch.synch_time = datetime.datetime.utcnow()
    new_synch.synch_count = chosen[1]
    db.db.session.add(new_synch)
    db.db.session.commit()


def _broadcast_add(key: db.Key):
    # Load the keyservers from the config file.
    keyservers = cfg.cfg.config.keyservers_synch
    for server in keyservers:
        assert isinstance(server, str)
        if not server.startswith("http"):
            # Force HTTPS by default, for security.
            server_url = "https://" + server
        else:
            server_url = server
            server = server.split("://")[1]

        try:
            r = requests.post(server_url + "/api/v{}/sync/new".format(cfg.API_VERSION), data={"key": key.armored})
        except requests.exceptions.ConnectionError:
            continue

        if r.status_code == 200:
            # good!
            continue
        elif r.status_code == 599:
            # Invalid key.
            break


def broadcast_add(key: db.Key):
    threading.Thread(target=_broadcast_add, args=(key,)).start()