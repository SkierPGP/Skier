import requests

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
